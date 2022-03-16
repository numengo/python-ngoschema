# -*- coding: utf-8 -*-
"""

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3
"""
from __future__ import print_function
from __future__ import unicode_literals

import weakref
import functools

from sqlalchemy.util import ScopedRegistry, ThreadLocalRegistry

from . import utils
from .decorators import assert_arg
from .protocols import ObjectProtocol, ArrayProtocol, SchemaMetaclass, with_metaclass
from .types import Tuple, Array
from .query import Query

_sessions = weakref.WeakValueDictionary()

_new_sessionid = utils.threadsafe_counter()


def _state_session(state):
    """Given an :class:`.InstanceState`, return the :class:`.Session`
        associated, if any.
    """
    if state.session_id:
        try:
            return _sessions[state.session_id]
        except KeyError:
            pass
    return None


class Session(with_metaclass(SchemaMetaclass)):
    _id = "https://numengo.org/ngoschema#/$defs/session/$defs/Session"

    def __init__(self, **kwargs):
        self._resolve_cname = functools.lru_cache(1024)(self._resolve_cname_cached)
        ObjectProtocol.__init__(self, value=kwargs)
        self._new = {}  # InstanceState->object, strong refs object
        self._deleted = {}  # same
        self._hash_key = _new_sessionid()
        _sessions[self._hash_key] = self

    def bind_repo(self, repo):
        self.repositories.append(repo)
        repo._session = self

    def get_or_create_repo(self, name, repo_registry=None):
        from .repositories import repositories_registry
        repo_registry = repo_registry or repositories_registry
        for r in self.repositories:
            if r.__class__.__name__ == name:
                return r
        # not found, create binded repository
        r = repo_registry.get(name)
        if r:
            return r(session=self)
        raise ValueError('no repository %s in registry %.' % (name, repo_registry))

    def get_or_create_repo_by_class(self, instance_class, repo_registry=None):
        from .repositories import repositories_registry
        repo_registry = repo_registry or repositories_registry
        for r in self.repositories:
            if r.instanceClass is instance_class:
                return r
        # not found, create binded repository
        # look first in repo registry
        for kr, r in repo_registry.items():
            if r.instanceClass is instance_class:
                return r(session=self)  # repo is binded at initialization
        raise ValueError('no instance_class %s in registry %.' % (instance_class, repo_registry))

    def resolve_cname(self, cname):
        return self._resolve_cname(cname)

    def _resolve_cname_cached(self, cname):
        from .models.instances import Entity
        cns = cname.split('.')
        rn = cns[0]
        cn = cns[1:]
        for repo in [r for r in self._repos if issubclass(r.instanceClass, Entity)]:
            if rn in repo:
                v = repo.resolve_fkey(rn)
                return v if not cn else v.resolve_cname(cn)
        raise Exception("Impossible to resolve '%s'" % cname)

    @assert_arg(1, Tuple, strDelimiter=',')
    def resolve_fkey(self, keys, object_class):
        for repo in [r for r in self.repositories if issubclass(r.instanceClass, object_class)]:
            if keys in repo:
                return repo.resolve_fkey(keys)
        else:
            raise Exception("Impossible to resolve '%s'" % keys)

    def query(self, *attrs, order_by=False, **attrs_value):
        """
        Make a `Query` on registered documents
        """
        return Query(self._chained.values()).filter(
            *attrs, order_by=order_by, **attrs_value)

    def commit(self):
        pass

    def close(selfself):
        pass

    def _add_bind(self, key, bind):
        self.__bind[key] = bind

    def query(self, *entities, **kwargs):
        """Return a new :class:`.Query` object corresponding to this
        :class:`.Session`."""

        return self._query_cls(entities, self, **kwargs)

    def expire(self, instance):
        """Expire the attributes on an instance.

        Marks the attributes of an instance as out of date. When an expired
        attribute is next accessed, a query will be issued to the
        :class:`.Session` object's current transactional context in order to
        load all expired attributes for the given instance.   Note that
        a highly isolated transaction will return the same values as were
        previously read in that same transaction, regardless of changes
        in database state outside of that transaction"""
        pass

    def add(self, instance):
        pass

    def expunge(self, instance):
        pass

    def delete(self, instance):
        pass

    def merge(self, instance, load=True):
        pass


class session_maker(object):
    """A configurable :class:`.Session` factory.

    The :class:`.sessionmaker` factory generates new
    :class:`.Session` objects when called, creating them given
    the configurational arguments established here.

    e.g.::

        # global scope
        Session = sessionmaker(autoflush=False)

        # later, in a local scope, create and use a session:
        sess = Session()

    Any keyword arguments sent to the constructor itself will override the
    "configured" keywords::

        Session = sessionmaker()

        # bind an individual session to a connection
        sess = Session(bind=connection)

    The class also includes a method :meth:`.configure`, which can
    be used to specify additional keyword arguments to the factory, which
    will take effect for subsequent :class:`.Session` objects generated.
    This is usually used to associate one or more :class:`.Engine` objects
    with an existing :class:`.sessionmaker` factory before it is first
    used::

        # application starts
        Session = sessionmaker()

        # ... later
        engine = create_engine('sqlite:///foo.db')
        Session.configure(bind=engine)

        sess = Session()

    .. seealso:

        :ref:`session_getting` - introductory text on creating
        sessions using :class:`.sessionmaker`.

    """

    def __init__(
        self,
        bind=None,
        class_=Session,
        autoflush=True,
        autocommit=False,
        expire_on_commit=True,
        info=None,
        **kw
    ):
        r"""Construct a new :class:`.sessionmaker`.

        All arguments here except for ``class_`` correspond to arguments
        accepted by :class:`.Session` directly.  See the
        :meth:`.Session.__init__` docstring for more details on parameters.

        :param bind: a :class:`.Engine` or other :class:`.Connectable` with
         which newly created :class:`.Session` objects will be associated.
        :param class\_: class to use in order to create new :class:`.Session`
         objects.  Defaults to :class:`.Session`.
        :param autoflush: The autoflush setting to use with newly created
         :class:`.Session` objects.
        :param autocommit: The autocommit setting to use with newly created
         :class:`.Session` objects.
        :param expire_on_commit=True: the expire_on_commit setting to use
         with newly created :class:`.Session` objects.
        :param info: optional dictionary of information that will be available
         via :attr:`.Session.info`.  Note this dictionary is *updated*, not
         replaced, when the ``info`` parameter is specified to the specific
         :class:`.Session` construction operation.

         .. versionadded:: 0.9.0

        :param \**kw: all other keyword arguments are passed to the
         constructor of newly created :class:`.Session` objects.

        """
        kw["bind"] = bind
        kw["autoflush"] = autoflush
        kw["autocommit"] = autocommit
        kw["expire_on_commit"] = expire_on_commit
        if info is not None:
            kw["info"] = info
        self.kw = kw
        # make our own subclass of the given class, so that
        # events can be associated with it specifically.
        self.class_ = type(class_.__name__, (class_,), {})

    def __call__(self, **local_kw):
        """Produce a new :class:`.Session` object using the configuration
        established in this :class:`.sessionmaker`.

        In Python, the ``__call__`` method is invoked on an object when
        it is "called" in the same way as a function::

            Session = sessionmaker()
            session = Session()  # invokes sessionmaker.__call__()

        """
        for k, v in self.kw.items():
            if k == "info" and "info" in local_kw:
                d = v.copy()
                d.update(local_kw["info"])
                local_kw["info"] = d
            else:
                local_kw.setdefault(k, v)
        return self.class_(**local_kw)

    def configure(self, **new_kw):
        """(Re)configure the arguments for this sessionmaker.

        e.g.::

            Session = sessionmaker()

            Session.configure(bind=create_engine('sqlite://'))
        """
        self.kw.update(new_kw)


def close_all_sessions():
    for sess in _sessions.values():
        sess.close()


class scoped_session(object):
    """Provides scoped management of :class:`.Session` objects.

    See :ref:`unitofwork_contextual` for a tutorial.

    """

    session_factory = None
    """The `session_factory` provided to `__init__` is stored in this
    attribute and may be accessed at a later time.  This can be useful when
    a new non-scoped :class:`.Session` or :class:`.Connection` to the
    database is needed."""

    def __init__(self, session_factory, scopefunc=None):
        """Construct a new :class:`.scoped_session`.

        :param session_factory: a factory to create new :class:`.Session`
         instances. This is usually, but not necessarily, an instance
         of :class:`.sessionmaker`.
        :param scopefunc: optional function which defines
         the current scope.   If not passed, the :class:`.scoped_session`
         object assumes "thread-local" scope, and will use
         a Python ``threading.local()`` in order to maintain the current
         :class:`.Session`.  If passed, the function should return
         a hashable token; this token will be used as the key in a
         dictionary in order to store and retrieve the current
         :class:`.Session`.

        """
        self.session_factory = session_factory

        if scopefunc:
            self.registry = ScopedRegistry(session_factory, scopefunc)
        else:
            self.registry = ThreadLocalRegistry(session_factory)

    def __call__(self, **kw):
        r"""Return the current :class:`.Session`, creating it
        using the :attr:`.scoped_session.session_factory` if not present.

        :param \**kw: Keyword arguments will be passed to the
         :attr:`.scoped_session.session_factory` callable, if an existing
         :class:`.Session` is not present.  If the :class:`.Session` is present
         and keyword arguments have been passed,
         :exc:`~sqlalchemy.exc.InvalidRequestError` is raised.

        """
        if kw:
            if self.registry.has():
                raise sa_exc.InvalidRequestError(
                    "Scoped session is already present; "
                    "no new arguments may be specified."
                )
            else:
                sess = self.session_factory(**kw)
                self.registry.set(sess)
                return sess
        else:
            return self.registry()

    def remove(self):
        """Dispose of the current :class:`.Session`, if present.

        This will first call :meth:`.Session.close` method
        on the current :class:`.Session`, which releases any existing
        transactional/connection resources still being held; transactions
        specifically are rolled back.  The :class:`.Session` is then
        discarded.   Upon next usage within the same scope,
        the :class:`.scoped_session` will produce a new
        :class:`.Session` object.

        """

        if self.registry.has():
            self.registry().close()
        self.registry.clear()

    def configure(self, **kwargs):
        """reconfigure the :class:`.sessionmaker` used by this
        :class:`.scoped_session`.

        See :meth:`.sessionmaker.configure`.

        """

        if self.registry.has():
            self._logger.warning(
                "At least one scoped session is already present. "
                " configure() can not affect sessions that have "
                "already been created."
            )

        self.session_factory.configure(**kwargs)


default_session = scoped_session(session_maker())()

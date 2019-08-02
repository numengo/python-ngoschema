<map version="freeplane 1.6.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="NUMENGO" FOLDED="false" ID="ID_1508363761" CREATED="1560152088771" MODIFIED="1560848402492" STYLE="oval">
<font SIZE="18"/>
<hook NAME="MapStyle">
    <properties fit_to_viewport="false" show_icon_for_attributes="true" edgeColorConfiguration="#808080ff,#ff0000ff,#0000ffff,#00ff00ff,#ff00ffff,#00ffffff,#7c0000ff,#00007cff,#007c00ff,#7c007cff,#007c7cff,#7c7c00ff"/>

<map_styles>
<stylenode LOCALIZED_TEXT="styles.root_node" STYLE="oval" UNIFORM_SHAPE="true" VGAP_QUANTITY="24.0 pt">
<font SIZE="24"/>
<stylenode LOCALIZED_TEXT="styles.predefined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="default" ICON_SIZE="12.0 pt" COLOR="#000000" STYLE="fork">
<font NAME="SansSerif" SIZE="10" BOLD="false" ITALIC="false"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.details"/>
<stylenode LOCALIZED_TEXT="defaultstyle.attributes">
<font SIZE="9"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.note" COLOR="#000000" BACKGROUND_COLOR="#ffffff" TEXT_ALIGN="LEFT"/>
<stylenode LOCALIZED_TEXT="defaultstyle.floating">
<edge STYLE="hide_edge"/>
<cloud COLOR="#f0f0f0" SHAPE="ROUND_RECT"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.user-defined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="styles.topic" COLOR="#18898b" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subtopic" COLOR="#cc3300" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subsubtopic" COLOR="#669900">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.important">
<icon BUILTIN="yes"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.AutomaticLayout" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="AutomaticLayout.level.root" COLOR="#000000" STYLE="oval" SHAPE_HORIZONTAL_MARGIN="10.0 pt" SHAPE_VERTICAL_MARGIN="10.0 pt">
<font SIZE="18"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,1" COLOR="#0033ff">
<font SIZE="16"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,2" COLOR="#00b439">
<font SIZE="14"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,3" COLOR="#990000">
<font SIZE="12"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,4" COLOR="#111111">
<font SIZE="10"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,5"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,6"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,7"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,8"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,9"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,10"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,11"/>
</stylenode>
</stylenode>
</map_styles>
</hook>
<hook NAME="AutomaticEdgeColor" COUNTER="28" RULE="ON_BRANCH_CREATION"/>
<node TEXT="description" POSITION="right" ID="ID_1178909789" CREATED="1560848446794" MODIFIED="1560848464840">
<edge COLOR="#00ffff"/>
<node TEXT="summary" ID="ID_649923253" CREATED="1560848465900" MODIFIED="1560848467947">
<node TEXT="describe all objects with a json-schema" ID="ID_537294669" CREATED="1548839960862" MODIFIED="1548839984521"/>
<node TEXT="classes built using a metaclass based on json-schema" ID="ID_1576261043" CREATED="1548839988033" MODIFIED="1548840037102">
<node TEXT="objects all share a common protocol" ID="ID_428275381" CREATED="1548840057324" MODIFIED="1548840065083"/>
<node TEXT="validators on getter/setters" ID="ID_1322675290" CREATED="1548840039026" MODIFIED="1548840056856"/>
</node>
<node TEXT="mini-ORM to manage the objects and their relationships" ID="ID_1296537918" CREATED="1548840071673" MODIFIED="1548840090379"/>
</node>
<node TEXT="usage" ID="ID_622339813" CREATED="1548840093388" MODIFIED="1560848514941">
<node TEXT="code generation" ID="ID_949439343" CREATED="1548840097559" MODIFIED="1548840100810">
<node TEXT="API" ID="ID_1213853189" CREATED="1548840125934" MODIFIED="1548840127888"/>
<node TEXT="SqlAlchemy models =&gt; physical storage" ID="ID_637222493" CREATED="1548840138518" MODIFIED="1548840164045"/>
</node>
<node TEXT="serialization/marshalling" ID="ID_856908774" CREATED="1548840103416" MODIFIED="1548840116451"/>
<node TEXT="allow to handle objects stored n files" ID="ID_330400133" CREATED="1548840170008" MODIFIED="1548853571553"/>
</node>
</node>
<node TEXT="missing packages" POSITION="right" ID="ID_1413842254" CREATED="1560152115567" MODIFIED="1560152121988">
<edge COLOR="#ff0000"/>
<node TEXT="pip install ruamel.yaml" ID="ID_815794768" CREATED="1560152122324" MODIFIED="1560152125241"/>
<node TEXT="pip install magic" ID="ID_1325349825" CREATED="1560152125728" MODIFIED="1560152131479">
<node ID="ID_1788694053" CREATED="1560152227509" MODIFIED="1560152227509"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span style="color: rgb(102, 102, 102); font-family: andale mono, lucida console, monospace; font-size: 14.401440620422363px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; background-color: rgb(255, 255, 255); text-decoration: none; display: inline !important; float: none"><font color="rgb(102, 102, 102)" face="andale mono, lucida console, monospace" size="14.401440620422363px">brew install libmagic</font></span>
  </body>
</html>
</richcontent>
</node>
</node>
</node>
<node TEXT="ideas" POSITION="right" ID="ID_137833754" CREATED="1560417953278" MODIFIED="1560417956029">
<edge COLOR="#0000ff"/>
<node TEXT="overload __eq__ and __ne__ for literals, HasCache" ID="ID_1367972448" CREATED="1560417983715" MODIFIED="1560419047430"/>
</node>
<node TEXT="SQL" POSITION="left" ID="ID_575445495" CREATED="1560848308116" MODIFIED="1560848310743">
<edge COLOR="#00ff00"/>
<node TEXT="https://use-the-index-luke.com/fr/table-des-matieres" ID="ID_1357782720" CREATED="1560848312712" MODIFIED="1560848312712" LINK="https://use-the-index-luke.com/fr/table-des-matieres"/>
</node>
<node TEXT="projects" POSITION="right" ID="ID_1259015571" CREATED="1548839942180" MODIFIED="1560848530967">
<edge COLOR="#7c7c00"/>
<node TEXT="ngoapi" ID="ID_485580582" CREATED="1548151395809" MODIFIED="1548151403571">
<node TEXT="decrire l API avec un json-schema" ID="ID_1496206483" CREATED="1548151404045" MODIFIED="1548151433229">
<node TEXT="arguments" ID="ID_359268500" CREATED="1548151433680" MODIFIED="1548151446253"/>
<node TEXT="response" ID="ID_1385121682" CREATED="1548151447074" MODIFIED="1548151453852"/>
</node>
<node TEXT="solutions" ID="ID_984448118" CREATED="1548153777917" MODIFIED="1548153784129">
<node TEXT="creer l API dynamiquement" ID="ID_886668551" CREATED="1548153784457" MODIFIED="1548153809128">
<node TEXT="mal debuggable" ID="ID_629747875" CREATED="1548153809447" MODIFIED="1548158079031"/>
<node TEXT="lourd" ID="ID_85518865" CREATED="1548158079483" MODIFIED="1548158095761"/>
</node>
<node TEXT="creer des templates de code" ID="ID_1171512522" CREATED="1548158098922" MODIFIED="1548158106087">
<node TEXT="tornado" ID="ID_1639608528" CREATED="1548158109885" MODIFIED="1548158112419"/>
<node TEXT="flask" ID="ID_1464077337" CREATED="1548158112625" MODIFIED="1548158114303"/>
</node>
<node TEXT="modele de endpoint" ID="ID_1099097451" CREATED="1548158141321" MODIFIED="1548158149193">
<node TEXT="description" ID="ID_1169401988" CREATED="1548158161751" MODIFIED="1548158170187"/>
<node TEXT="permission" ID="ID_118027164" CREATED="1548158170569" MODIFIED="1548158176067"/>
<node TEXT="target" ID="ID_493221397" CREATED="1548158177248" MODIFIED="1548158192115"/>
<node TEXT="methods" ID="ID_212563789" CREATED="1548158193289" MODIFIED="1548158198189">
<node ID="ID_1282220863" CREATED="1548158393996" MODIFIED="1548160210407"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <pre style="background-color: #2b2b2b; color: #a9b7c6; font-family: Menlo; font-size: 9.0pt">[<span style="color: #6a8759"><font color="#6a8759">'GET'</font></span><span style="color: #cc7832"><font color="#cc7832">, </font></span><span style="color: #6a8759"><font color="#6a8759">'LIST'</font></span><span style="color: #cc7832"><font color="#cc7832">, </font></span><span style="color: #6a8759"><font color="#6a8759">'PATCH'</font></span><span style="color: #cc7832"><font color="#cc7832">, </font></span><span style="color: #6a8759"><font color="#6a8759">'PUT', 'POST<content ename="content"/></font></span><span style="color: #cc7832"><font color="#cc7832">, </font></span><span style="color: #6a8759"><font color="#6a8759">'DELETE'</font></span>]</pre>
  </body>
</html>
</richcontent>
</node>
</node>
<node TEXT="parameters" ID="ID_331635235" CREATED="1548158628916" MODIFIED="1548158632356">
<node TEXT="parameter" ID="ID_399033274" CREATED="1548158664608" MODIFIED="1548158668828">
<node TEXT="methods" ID="ID_1471353467" CREATED="1548158669548" MODIFIED="1548158700638"/>
<node TEXT="required" ID="ID_1855223735" CREATED="1548158705104" MODIFIED="1548158712600"/>
<node TEXT="default" ID="ID_1426778197" CREATED="1548158707769" MODIFIED="1548158715012"/>
<node TEXT="type" ID="ID_1311015147" CREATED="1548158716044" MODIFIED="1548158719526"/>
<node TEXT="data_type" ID="ID_1823424113" CREATED="1548158754336" MODIFIED="1548158787821">
<node TEXT="KEY" ID="ID_984771962" CREATED="1548158788135" MODIFIED="1548158789864"/>
<node TEXT="Argument" ID="ID_330317576" CREATED="1548158795252" MODIFIED="1548158799413"/>
<node TEXT="Filter" ID="ID_1935264644" CREATED="1548158800369" MODIFIED="1548158803651">
<node TEXT="SearchFilter" ID="ID_1069571967" CREATED="1548158808982" MODIFIED="1548158812207">
<node TEXT="db_fields" ID="ID_509114245" CREATED="1548158920802" MODIFIED="1548158925584"/>
</node>
<node TEXT="DataFilter" ID="ID_1344907112" CREATED="1548158812457" MODIFIED="1548158817462"/>
<node TEXT="AnchorFilter" ID="ID_1243513938" CREATED="1548158829105" MODIFIED="1548158833203">
<node TEXT="filter on objects related to a resource" ID="ID_1321952351" CREATED="1548158973456" MODIFIED="1548158986516"/>
</node>
</node>
</node>
</node>
</node>
<node TEXT="response" ID="ID_818495038" CREATED="1548158199732" MODIFIED="1548158208173"/>
<node TEXT="response_list" ID="ID_942844709" CREATED="1548158208456" MODIFIED="1548158216082">
<node TEXT="&apos;=response" ID="ID_1632326950" CREATED="1548159211134" MODIFIED="1548159221647"/>
</node>
<node TEXT="uri" ID="ID_1191444997" CREATED="1548158264867" MODIFIED="1548158266362"/>
</node>
<node TEXT="component" ID="ID_1274169793" CREATED="1548158650866" MODIFIED="1548158655195">
<node TEXT="list_variables" ID="ID_1847275179" CREATED="1548159236913" MODIFIED="1548163947262"/>
<node TEXT="list_parameters" ID="ID_1785227025" CREATED="1548163947821" MODIFIED="1548163955955"/>
</node>
<node TEXT="endpoint" ID="ID_345943683" CREATED="1548161023391" MODIFIED="1548161036201">
<node TEXT="uri" ID="ID_1878522052" CREATED="1548161057692" MODIFIED="1548161059500"/>
<node TEXT="arguments" ID="ID_773590655" CREATED="1548161037348" MODIFIED="1548161075282"/>
<node TEXT="response" ID="ID_220082147" CREATED="1548161038956" MODIFIED="1548161079800"/>
</node>
<node TEXT="resource = object" ID="ID_366638700" CREATED="1548161084261" MODIFIED="1548161098165">
<node TEXT="methods" ID="ID_793428517" CREATED="1548161499015" MODIFIED="1548161502195">
<node TEXT="list" ID="ID_404252026" CREATED="1548161104235" MODIFIED="1548161108334"/>
<node TEXT="get" ID="ID_1319323526" CREATED="1548161113181" MODIFIED="1548161115490"/>
<node TEXT="post" ID="ID_185380959" CREATED="1548161117362" MODIFIED="1548161127396">
<node TEXT="create" ID="ID_205611725" CREATED="1548161949437" MODIFIED="1548161953004"/>
</node>
<node TEXT="put" ID="ID_1943472448" CREATED="1548161108861" MODIFIED="1548161112572">
<node TEXT="patch or create" ID="ID_643022508" CREATED="1548161955629" MODIFIED="1548161969750"/>
</node>
<node TEXT="patch" ID="ID_404946845" CREATED="1548161115696" MODIFIED="1548161942739">
<icon BUILTIN="yes"/>
<node TEXT="when you want to update a resource with PUT request, you have to send the full payload as the request whereas with PATCH, you only send the parameters which you want to update" ID="ID_231504188" CREATED="1548161847991" MODIFIED="1548161849506"/>
</node>
<node TEXT="delete" ID="ID_138966085" CREATED="1548161131207" MODIFIED="1548161133043"/>
<node TEXT="uri" ID="ID_1491709695" CREATED="1548161624212" MODIFIED="1548161627456"/>
<node ID="ID_407237717" CREATED="1548162138259" MODIFIED="1548162138259"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span style="color: rgb(36, 39, 41); font-family: Arial, Helvetica Neue, Helvetica, sans-serif; font-size: 15px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; background-color: rgb(255, 255, 255); text-decoration: none; display: inline !important; float: none"><font color="rgb(36, 39, 41)" face="Arial, Helvetica Neue, Helvetica, sans-serif" size="15px">If your endpoint returns a collection, you could implement searching/filtering/sorting using query strings</font></span>
  </body>
</html>
</richcontent>
<node TEXT="search / filter / sorting" ID="ID_753150413" CREATED="1548162192388" MODIFIED="1548162201609"/>
</node>
<node TEXT="+ object methods" ID="ID_373408730" CREATED="1548162309137" MODIFIED="1548162317147">
<node TEXT="arguments" ID="ID_747469885" CREATED="1548162320544" MODIFIED="1548162332681"/>
<node TEXT="response" ID="ID_458586528" CREATED="1548162372969" MODIFIED="1548162376237">
<node TEXT="outputs" ID="ID_1921205295" CREATED="1548162410811" MODIFIED="1548162413967"/>
</node>
</node>
</node>
<node TEXT="keys" ID="ID_830607340" CREATED="1548161692623" MODIFIED="1548162500622">
<node TEXT="get_keys()" ID="ID_1947112424" CREATED="1548162960738" MODIFIED="1548162964974">
<node TEXT="class method" ID="ID_769848110" CREATED="1548162965929" MODIFIED="1548162968773"/>
</node>
</node>
<node TEXT="search / filter / sorting" ID="ID_164450923" CREATED="1548162450211" MODIFIED="1548162463878"/>
<node TEXT="ordering" ID="ID_453764504" CREATED="1548162900978" MODIFIED="1548162907041"/>
<node TEXT="access_filter_list" ID="ID_1566409954" CREATED="1548162914724" MODIFIED="1548162920442"/>
<node TEXT="limit" ID="ID_787698406" CREATED="1548162927384" MODIFIED="1548162929906"/>
</node>
</node>
</node>
<node TEXT="GUI" ID="ID_976710226" CREATED="1548765259996" MODIFIED="1549442043412">
<node TEXT="Kivy" FOLDED="true" ID="ID_1216850082" CREATED="1548765263645" MODIFIED="1548765308250" LINK="http://kivy.org/">
<node TEXT="native" ID="ID_845008247" CREATED="1548765366864" MODIFIED="1548765368976">
<node TEXT="android" ID="ID_1182173320" CREATED="1548765265777" MODIFIED="1548765267882"/>
<node TEXT="iphone" ID="ID_187213438" CREATED="1548765268625" MODIFIED="1548765271799"/>
<node TEXT="pc" ID="ID_1030001279" CREATED="1548765273451" MODIFIED="1548765287003"/>
<node TEXT="mac" ID="ID_1135480552" CREATED="1548765287333" MODIFIED="1548765288464"/>
</node>
<node TEXT="events" ID="ID_906764953" CREATED="1548765383298" MODIFIED="1548765386795"/>
<node TEXT="layouts" ID="ID_427575360" CREATED="1548765400669" MODIFIED="1548765404549">
<node TEXT="widgets" ID="ID_1781965273" CREATED="1548765387110" MODIFIED="1548765395069">
<node TEXT="canvas" ID="ID_1416930089" CREATED="1548766564660" MODIFIED="1548766713083"/>
<node TEXT="Label" ID="ID_1161021566" CREATED="1548767409739" MODIFIED="1548768129712">
<node TEXT="properties" ID="ID_240472110" CREATED="1548769385173" MODIFIED="1548769391031">
<node TEXT="font_size" ID="ID_1219175720" CREATED="1548767426338" MODIFIED="1548767431523"/>
<node TEXT="center_x" ID="ID_1919292248" CREATED="1548767431773" MODIFIED="1548767434372"/>
<node TEXT="top" ID="ID_1013070192" CREATED="1548767434712" MODIFIED="1548767435976"/>
<node TEXT="text" ID="ID_856500098" CREATED="1548767436243" MODIFIED="1548767437755"/>
</node>
</node>
<node TEXT="Rectangle" ID="ID_776105463" CREATED="1548767413227" MODIFIED="1548768136246">
<node TEXT="properties" ID="ID_841992683" CREATED="1548769385173" MODIFIED="1548769391031">
<node TEXT="pos" ID="ID_547118402" CREATED="1548767417794" MODIFIED="1548767418575"/>
<node TEXT="size" ID="ID_1218044324" CREATED="1548767418865" MODIFIED="1548767423981"/>
</node>
</node>
<node TEXT="Button" FOLDED="true" ID="ID_590413414" CREATED="1548768121095" MODIFIED="1548768123615">
<node TEXT="properties" ID="ID_59554881" CREATED="1548769370071" MODIFIED="1548769371865">
<node TEXT="text" ID="ID_379737307" CREATED="1548768138947" MODIFIED="1548768140268"/>
<node TEXT="text_size" ID="ID_981435536" CREATED="1548768140474" MODIFIED="1548768145235"/>
<node TEXT="font_size" ID="ID_1985200495" CREATED="1548768145557" MODIFIED="1548768148253"/>
<node TEXT="markup" ID="ID_512289138" CREATED="1548768148627" MODIFIED="1548768151504"/>
</node>
</node>
<node TEXT="size" ID="ID_809305551" CREATED="1548767512525" MODIFIED="1548767522295">
<node TEXT="tuple" ID="ID_1759347424" CREATED="1548767523299" MODIFIED="1548767526128"/>
</node>
<node TEXT="center" ID="ID_1269611634" CREATED="1548767631133" MODIFIED="1548767633075"/>
</node>
<node TEXT="properties" ID="ID_1933281367" CREATED="1548769353096" MODIFIED="1548769358427">
<node TEXT="orientation" ID="ID_1432887752" CREATED="1548769359050" MODIFIED="1548769363585"/>
<node TEXT="padding" ID="ID_4247800" CREATED="1548769364205" MODIFIED="1548769365595"/>
</node>
</node>
<node TEXT="works well with Twisted" ID="ID_514949480" CREATED="1548769606130" MODIFIED="1548769614540"/>
</node>
<node TEXT="ForeignKey" ID="ID_315795303" CREATED="1548839686357" MODIFIED="1548839694759">
<node TEXT="key" ID="ID_829239539" CREATED="1548839695024" MODIFIED="1548839699598"/>
<node TEXT="targetSchemaUri" ID="ID_1649412261" CREATED="1548839701834" MODIFIED="1548839709178"/>
<node TEXT="" ID="ID_212160090" CREATED="1548839709469" MODIFIED="1548839709469"/>
</node>
</node>
<node TEXT="service web android" FOLDED="true" ID="ID_1974230155" CREATED="1548765222621" MODIFIED="1549442052758">
<node TEXT="python-from-android" ID="ID_792610073" CREATED="1548765251159" MODIFIED="1548765256015"/>
</node>
<node TEXT="permissions" FOLDED="true" ID="ID_731506319" CREATED="1548766193848" MODIFIED="1549442055773">
<node TEXT="python lib &apos;permission&apos;" ID="ID_1864362035" CREATED="1548766198058" MODIFIED="1548766211370" LINK="https://pypi.org/project/permission/">
<node TEXT="Rule" ID="ID_754536997" CREATED="1548766217935" MODIFIED="1548766219680">
<node TEXT="check" ID="ID_1809988375" CREATED="1548766236818" MODIFIED="1548766238611"/>
<node TEXT="deny" ID="ID_627415690" CREATED="1548766239062" MODIFIED="1548766239985"/>
<node TEXT="base" ID="ID_308451962" CREATED="1548766422839" MODIFIED="1548766424059"/>
</node>
<node TEXT="Permission" ID="ID_738206242" CREATED="1548766425501" MODIFIED="1548766428392">
<node TEXT="rule" ID="ID_328763584" CREATED="1548766433913" MODIFIED="1548766436216"/>
</node>
</node>
</node>
<node TEXT="candidates" FOLDED="true" ID="ID_534577912" CREATED="1534497976803" MODIFIED="1560848536402">
<icon BUILTIN="bookmark"/>
<node TEXT="pull" ID="ID_1738986411" CREATED="1534497993554" MODIFIED="1534865608426" LINK="https://github.com/toastdriven/restless"/>
<node TEXT="falcon" ID="ID_828329392" CREATED="1534498027324" MODIFIED="1534843015690" LINK="https://github.com/falconry/falcon"/>
<node TEXT="tornado" ID="ID_1551243824" CREATED="1534583561460" MODIFIED="1560848536401"/>
<node TEXT="Dash" FOLDED="true" ID="ID_3478372" CREATED="1534581582167" MODIFIED="1534581604605" LINK="https://plot.ly/products/dash/">
<icon BUILTIN="messagebox_warning"/>
<icon BUILTIN="idea"/>
<node TEXT="for building analytical web applications" ID="ID_819735763" CREATED="1534581625323" MODIFIED="1534581626456"/>
<node TEXT="Dash applications are web servers that run Flask and communicate with JSON packets over HTTP requests. Their frontend renders components with React.js." ID="ID_1853463935" CREATED="1534581661032" MODIFIED="1534581661538"/>
</node>
<node TEXT="quokka CMS/CMF" ID="ID_1344327373" CREATED="1534583407251" MODIFIED="1534583431070" LINK="https://github.com/rochacbruno/quokka"/>
</node>
<node TEXT="NgoSchema" FOLDED="true" ID="ID_147024947" CREATED="1549455268624" MODIFIED="1549874576645" LINK="https://github.com/numengo/python-ngoschema/tree/devel">
<node TEXT="opensource" ID="ID_850743903" CREATED="1549456135700" MODIFIED="1549456139993"/>
<node TEXT="description" ID="ID_514322876" CREATED="1549455304765" MODIFIED="1549455322941">
<node TEXT="automatic class-based binding to JSON schemas for use in python" ID="ID_153838926" CREATED="1549455328691" MODIFIED="1549455427998">
<node TEXT="extends python-jsonschema-objects" ID="ID_551829138" CREATED="1549455545061" MODIFIED="1549455557189"/>
<node TEXT="enriched metamodel" ID="ID_1151863223" CREATED="1549455560417" MODIFIED="1549456095157">
<node ID="ID_1193911184" CREATED="1549456096318" MODIFIED="1549456096318"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      to describe complex classes
    </p>
  </body>
</html>
</richcontent>
<node TEXT="inheritance" ID="ID_260838437" CREATED="1549455582811" MODIFIED="1549982437768"/>
</node>
<node TEXT="to describe database persistance" ID="ID_733742575" CREATED="1549456100038" MODIFIED="1549456119155"/>
</node>
<node TEXT="create classes sharing a same protocol" ID="ID_628626851" CREATED="1549455595989" MODIFIED="1549455614067">
<node TEXT="automatic setter/getter with proper validators" ID="ID_382206093" CREATED="1549455615298" MODIFIED="1549455640183"/>
</node>
<node TEXT="allow to create hybrid classes" ID="ID_1529958465" CREATED="1549455671414" MODIFIED="1549455679646">
<node TEXT="described by a json schema" ID="ID_89064089" CREATED="1549455680466" MODIFIED="1549455884378"/>
<node TEXT="+ implementation in python" ID="ID_1991471766" CREATED="1549455884941" MODIFIED="1549455894178">
<node TEXT="override of setters/getters" ID="ID_369885876" CREATED="1549455897191" MODIFIED="1549455904552"/>
<node TEXT="business methods" ID="ID_1676661307" CREATED="1549455906927" MODIFIED="1549455925200"/>
</node>
</node>
<node TEXT="complex types" ID="ID_1249724346" CREATED="1549982445114" MODIFIED="1549982452490">
<node TEXT="path" ID="ID_858801067" CREATED="1549982452707" MODIFIED="1549982454762"/>
<node TEXT="date" ID="ID_653735894" CREATED="1549982454982" MODIFIED="1549982468930"/>
<node TEXT="datetime" ID="ID_431791643" CREATED="1549982469169" MODIFIED="1549982470932"/>
</node>
<node TEXT="automatically decorated" ID="ID_1619131472" CREATED="1549973873135" MODIFIED="1549973881838">
<node TEXT="logging" ID="ID_1021646871" CREATED="1549973882108" MODIFIED="1549973884470"/>
<node TEXT="exception handling" ID="ID_206166011" CREATED="1549973884637" MODIFIED="1549973889666"/>
</node>
<node TEXT="templated literal strings" ID="ID_1023397498" CREATED="1549973908887" MODIFIED="1549973918372"/>
</node>
<node TEXT="marshalling / serialization" ID="ID_440053977" CREATED="1549456011642" MODIFIED="1549456032777">
<node TEXT="json" ID="ID_1519209909" CREATED="1549456033493" MODIFIED="1549456041344"/>
<node TEXT="yaml" ID="ID_502019481" CREATED="1549456041586" MODIFIED="1549456043669"/>
<node TEXT="user serializers / deserializers" ID="ID_1194961852" CREATED="1549456043919" MODIFIED="1549456065438"/>
</node>
<node TEXT="ORM to manage the created instances" ID="ID_394476520" CREATED="1549455323869" MODIFIED="1549455948664">
<node TEXT="to perform queries" ID="ID_815628099" CREATED="1549455970090" MODIFIED="1549455979297"/>
</node>
</node>
<node TEXT="examples" ID="ID_768723510" CREATED="1549982510267" MODIFIED="1549985032731">
<node TEXT="schema simplifie" ID="ID_1011379087" CREATED="1549982518851" MODIFIED="1549982528096">
<node TEXT="MyClass" ID="ID_27495990" CREATED="1549985006715" MODIFIED="1549985012555"/>
</node>
<node TEXT="1" OBJECT="java.lang.Long|1" ID="ID_1357944034" CREATED="1549985033748" MODIFIED="1549985064597">
<node TEXT="MyClass" ID="ID_247978582" CREATED="1549982528939" MODIFIED="1549982533364">
<node TEXT="myInt" ID="ID_588161049" CREATED="1549982534177" MODIFIED="1549982539564"/>
</node>
<node TEXT="foo.myInt=1" ID="ID_1247487824" CREATED="1549985076019" MODIFIED="1549985098806">
<node TEXT="assert foo.myInt==1" ID="ID_1849076965" CREATED="1549985099641" MODIFIED="1549985110710"/>
</node>
<node TEXT="with Error" ID="ID_51521247" CREATED="1549985217762" MODIFIED="1549985222975">
<node TEXT="foo.myInt = &apos;hello&apos;" ID="ID_724297970" CREATED="1549985115119" MODIFIED="1549985215352">
<node TEXT="assert foo.myString==&apos;hello&apos;" ID="ID_1929342578" CREATED="1549985132284" MODIFIED="1549985144254"/>
</node>
</node>
</node>
<node TEXT="2" OBJECT="java.lang.Long|2" ID="ID_1400977011" CREATED="1549985047090" MODIFIED="1549985068031">
<node TEXT="MyClass" ID="ID_631757237" CREATED="1549984979050" MODIFIED="1549984983871">
<node TEXT="myInt" ID="ID_463007425" CREATED="1549984984637" MODIFIED="1549984987788">
<node TEXT="min 0" ID="ID_1114862107" CREATED="1549984988546" MODIFIED="1549984994086"/>
<node TEXT="max 9" ID="ID_380143664" CREATED="1549984994598" MODIFIED="1549985002563"/>
</node>
</node>
</node>
<node TEXT="3" OBJECT="java.lang.Long|3" ID="ID_1586684462" CREATED="1549985055887" MODIFIED="1549985069658">
<node TEXT="MyClass" ID="ID_1878071756" CREATED="1549985870876" MODIFIED="1549985881375">
<node TEXT="myString" ID="ID_1217867277" CREATED="1549985882883" MODIFIED="1549985886680"/>
<node TEXT="myStringUpperCase" ID="ID_1258071272" CREATED="1549985887285" MODIFIED="1549985922265"/>
</node>
</node>
<node TEXT="4" OBJECT="java.lang.Long|4" ID="ID_1138526876" CREATED="1549985059145" MODIFIED="1549985071154">
<node TEXT="MyClass" ID="ID_410305345" CREATED="1549986398115" MODIFIED="1549986402569">
<node TEXT="myPath" ID="ID_1379482998" CREATED="1549986403259" MODIFIED="1549986405596"/>
<node TEXT="myDate" ID="ID_1810636428" CREATED="1549986405846" MODIFIED="1549986408001"/>
<node TEXT="myDatetime" ID="ID_889371115" CREATED="1549986408245" MODIFIED="1549986413127"/>
</node>
</node>
<node TEXT="5" OBJECT="java.lang.Long|5" ID="ID_814428370" CREATED="1549986393494" MODIFIED="1549986650759">
<node TEXT="MyClass" ID="ID_1047051177" CREATED="1549986651590" MODIFIED="1549986655310">
<node TEXT="myMember" ID="ID_1199999596" CREATED="1549986655602" MODIFIED="1549986671027"/>
<node TEXT="get_myMember" ID="ID_802420146" CREATED="1549986671923" MODIFIED="1549986679974"/>
</node>
</node>
</node>
<node TEXT="objects" FOLDED="true" ID="ID_1096874576" CREATED="1549456309942" MODIFIED="1549529332857">
<node TEXT="classbuilder" ID="ID_950349882" CREATED="1549456315392" MODIFIED="1549456318507">
<node TEXT="ProtocolBase" ID="ID_1264833866" CREATED="1549456326724" MODIFIED="1549456330566"/>
<node TEXT="ClassBuilder" ID="ID_572253054" CREATED="1549456322477" MODIFIED="1549456326397"/>
</node>
<node TEXT="object_factory" ID="ID_879842803" CREATED="1549456916156" MODIFIED="1549456926844">
<node TEXT="pour les transforms??" ID="ID_1537763291" CREATED="1549456944476" MODIFIED="1549456955906"/>
<node TEXT="to create objects from documents, to handle their transforms" ID="ID_10660272" CREATED="1549529213812" MODIFIED="1549529258439"/>
</node>
<node TEXT="object_loader" ID="ID_1668052409" CREATED="1549456927109" MODIFIED="1549456931648">
<node TEXT="???" ID="ID_861888153" CREATED="1549456936167" MODIFIED="1549456938509"/>
</node>
<node TEXT="ForeignKey" ID="ID_716660605" CREATED="1549456332883" MODIFIED="1549456336588"/>
<node TEXT="Metadata" ID="ID_1784898536" CREATED="1549456336937" MODIFIED="1549456343463">
<node TEXT="source" ID="ID_837598648" CREATED="1549457457975" MODIFIED="1549457462077" LINK="http://marciazeng.slis.kent.edu/metadatabasics/types.htm"/>
<node TEXT="descriptive" ID="ID_786132670" CREATED="1549457304853" MODIFIED="1549457307772">
<node TEXT="describes a resource for purposes such as discovery and identification. It can include elements such as title, abstract, author, and keywords" ID="ID_1718729296" CREATED="1549457308453" MODIFIED="1549457322920"/>
</node>
<node TEXT="structural" ID="ID_111583380" CREATED="1549457330360" MODIFIED="1549457332850">
<node TEXT="indicates how compound objects are put together, for example, how pages are ordered to form chapters." ID="ID_216596281" CREATED="1549457344973" MODIFIED="1549457346688"/>
</node>
<node TEXT="administrative" ID="ID_1114981707" CREATED="1549457348716" MODIFIED="1549457352129">
<node TEXT="provides information to help manage a resource, such as when and how it was created, file type and other technical information, and who can access it" ID="ID_1239559334" CREATED="1549457366079" MODIFIED="1549457366747"/>
<node TEXT="Preservation metadata" ID="ID_950067251" CREATED="1549457414705" MODIFIED="1549457421364">
<node TEXT="contains information needed to archive and preserve a resource." ID="ID_385302039" CREATED="1549457422093" MODIFIED="1549457423209"/>
</node>
<node TEXT="Rights management metadata" ID="ID_492412645" CREATED="1549457436780" MODIFIED="1549457443900">
<node TEXT="deals with intellectual property rights" ID="ID_1035639386" CREATED="1549457444788" MODIFIED="1549457445662"/>
</node>
</node>
</node>
<node TEXT="Permission" ID="ID_1605191273" CREATED="1549457622644" MODIFIED="1549457625178">
<node TEXT="permissions" ID="ID_1556462348" CREATED="1548765212464" MODIFIED="1549442060045" LINK="https://pythonhosted.org/python-stdnet/examples/permissions.html">
<node TEXT="https://developers.evrythng.com/docs/using-the-dashboard-roles-permissions-schemas" ID="ID_536291990" CREATED="1549457904932" MODIFIED="1549457904932" LINK="https://developers.evrythng.com/docs/using-the-dashboard-roles-permissions-schemas"/>
<node TEXT="Roles" ID="ID_369366490" CREATED="1548765616195" MODIFIED="1548765628534">
<node TEXT="name" ID="ID_704710811" CREATED="1548765689469" MODIFIED="1548765691097"/>
<node TEXT="owner" ID="ID_1211767742" CREATED="1548765691649" MODIFIED="1548765693651"/>
<node TEXT="permissions" ID="ID_1052949623" CREATED="1548765708083" MODIFIED="1548765713073">
<node TEXT="set(Permission)" ID="ID_645375642" CREATED="1548765715253" MODIFIED="1548765723537"/>
</node>
<node TEXT="add_permission(resource, operation)" ID="ID_1040884747" CREATED="1548765753652" MODIFIED="1548765769554">
<node TEXT="Add a new Permission for resource to perform an operation. The resource can be either an object or a model." ID="ID_578226562" CREATED="1548765778513" MODIFIED="1548765780132"/>
</node>
<node TEXT="assign_to(subject)" ID="ID_93883721" CREATED="1548765725624" MODIFIED="1548765750033">
<node TEXT="Assign this Role to subject" ID="ID_669191484" CREATED="1548765789371" MODIFIED="1548765790474"/>
</node>
</node>
<node TEXT="Permissions" ID="ID_1610949986" CREATED="1548765628930" MODIFIED="1548765633438"/>
<node TEXT="Operations" ID="ID_1063833289" CREATED="1548765638813" MODIFIED="1548765641512">
<node TEXT="read" ID="ID_204140937" CREATED="1548765661399" MODIFIED="1548765663109"/>
<node TEXT="write" ID="ID_1549033835" CREATED="1548765663545" MODIFIED="1548765666286"/>
<node TEXT="delete" ID="ID_1995237516" CREATED="1548765666864" MODIFIED="1548765668000"/>
</node>
<node TEXT="Subjects" ID="ID_1188798190" CREATED="1548765641673" MODIFIED="1548765643370">
<node TEXT="Group" ID="ID_910023323" CREATED="1548765802708" MODIFIED="1548765807677">
<node TEXT="name" ID="ID_1523324334" CREATED="1548765847017" MODIFIED="1548765847934">
<node TEXT="Group name. If the group is for a signle user, it can be the user username" ID="ID_369128151" CREATED="1548765891688" MODIFIED="1548765892682"/>
<node TEXT="&apos;=None" ID="ID_9248417" CREATED="1548765893136" MODIFIED="1548765908430"/>
</node>
<node TEXT="user" ID="ID_1474762823" CREATED="1548765848432" MODIFIED="1548765849317">
<node TEXT="A group is always owned by a User. For example the admin group for a website is owned by the website user" ID="ID_159124553" CREATED="1548765922606" MODIFIED="1548765923755"/>
</node>
<node TEXT="users" ID="ID_1082766017" CREATED="1548765853850" MODIFIED="1548765855961">
<node TEXT="The stdnet.odm.ManyToManyField for linking User and Group." ID="ID_377492980" CREATED="1548765938654" MODIFIED="1548765939460"/>
</node>
</node>
<node TEXT="User" ID="ID_1600060421" CREATED="1548765808038" MODIFIED="1548765811084">
<node TEXT="username" ID="ID_1222010259" CREATED="1548765837684" MODIFIED="1548765841729"/>
</node>
</node>
</node>
</node>
</node>
<node TEXT="schemas" FOLDED="true" ID="ID_1539681653" CREATED="1549456345238" MODIFIED="1549456348551">
<node TEXT="Metadata" ID="ID_40508694" CREATED="1549456348794" MODIFIED="1549456356593"/>
<node TEXT="RelationShip" ID="ID_1719274656" CREATED="1549456359889" MODIFIED="1549456890675"/>
<node TEXT="ForeignKey" ID="ID_588369151" CREATED="1549456891438" MODIFIED="1549456899350"/>
</node>
</node>
<node TEXT="NgoPck" ID="ID_1042226213" CREATED="1549455276583" MODIFIED="1549455280585">
<node TEXT="private" ID="ID_1104009563" CREATED="1549456131946" MODIFIED="1549456146929"/>
<node TEXT="description" ID="ID_226624935" CREATED="1549456147466" MODIFIED="1549456151276">
<node TEXT="packaging and distribution of numengo solution" ID="ID_145485290" CREATED="1549456152741" MODIFIED="1549529127203"/>
</node>
</node>
<node TEXT="NgoCi" ID="ID_786231447" CREATED="1549455280905" MODIFIED="1549455287874">
<node TEXT="private" ID="ID_712475594" CREATED="1549456195793" MODIFIED="1549456197523"/>
<node TEXT="description" ID="ID_1541111614" CREATED="1549456197866" MODIFIED="1549456263896">
<node TEXT="tools for managing projects and their dependencies" ID="ID_1829989431" CREATED="1549456264267" MODIFIED="1549529152418">
<node TEXT="build" ID="ID_665540433" CREATED="1549456282258" MODIFIED="1549456284381"/>
</node>
<node TEXT="project boilerplate" ID="ID_792244675" CREATED="1549529157074" MODIFIED="1549529172718"/>
</node>
</node>
<node TEXT="NgoMf" ID="ID_1834232753" CREATED="1549455288187" MODIFIED="1549455294033">
<node TEXT="private" ID="ID_1556601457" CREATED="1549456131946" MODIFIED="1549456146929"/>
<node TEXT="description" ID="ID_1801601746" CREATED="1549456147466" MODIFIED="1549456151276">
<node TEXT="tools for code generation of numengo objects" ID="ID_489367804" CREATED="1549456152741" MODIFIED="1549456257979"/>
<node TEXT="tools for" ID="ID_416862288" CREATED="1549529183720" MODIFIED="1549529209845"/>
</node>
</node>
</node>
<node TEXT="Ideas for NUMENGO" FOLDED="true" POSITION="right" ID="ID_1951444762" CREATED="1539956303171" MODIFIED="1540280422287">
<edge COLOR="#7c0000"/>
<node TEXT="API" ID="ID_1848375593" CREATED="1540280423111" MODIFIED="1540280427059">
<node TEXT="Response" ID="ID_1318448038" CREATED="1540280427608" MODIFIED="1540280505370"/>
<node TEXT="Input / Arguments" ID="ID_1576903240" CREATED="1540280432537" MODIFIED="1540280564950">
<node TEXT="GET" ID="ID_1608432015" CREATED="1540280446543" MODIFIED="1540280448322"/>
<node TEXT="POST" ID="ID_761400137" CREATED="1540280448678" MODIFIED="1540280450092"/>
<node TEXT="Header" ID="ID_361420708" CREATED="1540280535772" MODIFIED="1540280539067"/>
<node TEXT="Query" ID="ID_581129378" CREATED="1540280531002" MODIFIED="1540280535315"/>
</node>
<node TEXT="CrudResource" ID="ID_591045213" CREATED="1540296962274" MODIFIED="1540296971235">
<node TEXT="Resource" ID="ID_946996963" CREATED="1540306583729" MODIFIED="1540306587650">
<node TEXT="defined by a single class inheriting from CRUDResource" ID="ID_1961721132" CREATED="1540306604727" MODIFIED="1540306605679"/>
<node FOLDED="true" ID="ID_83435447" CREATED="1540306618312" MODIFIED="1540306618312"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        A Meta section, containing at least four fields: description, permission, dbmodel and response_model. More customization options are available, see below.
      </li>
    </ul>
  </body>
</html>
</richcontent>
<node ID="ID_79163412" CREATED="1540307352703" MODIFIED="1540307352703"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        description (required): A string used to describe the entity managed by the resource. This will be used in contexts like &quot;Creates or updates a &lt;description&gt;&quot; for the PUT endpoint.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_30018248" CREATED="1540307352703" MODIFIED="1540307352703"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        dbmodel (required): A SQLAlchemy model. This model fields should have the same names as the fields of the resource and a mapping will be generated between these two kind of fields.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1077122106" CREATED="1540307352703" MODIFIED="1540307352703"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        response_model (required): A flask model that will be used for marshaling for GET and LIST operations. It will not be used for other methods.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_845377555" CREATED="1540307352703" MODIFIED="1540307352703"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        response_model<em>_</em>list (optional, default: &lt;same as response_model&gt;): An optional override for response_model that will be used only for LIST.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1730006292" CREATED="1540307352704" MODIFIED="1540307352704"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        methods (optional, default: GET, LIST, DELETE, PUT): The list of methods to be generated. Up to five methods may be chosen (the four defaults one, + POST).
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1136107403" CREATED="1540307352704" MODIFIED="1540307352704"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        param_path (optional, default: &lt;generated from Key fields&gt;): The path to append to the dir resource in order to get the entity resource. This should be a string starting with '/', suitable for python .format() function, and with parameters corresponding to the name of the keys.
      </li>
    </ul>
  </body>
</html>
</richcontent>
<node TEXT="class MyResource(CRUDResource):&#xa;    class Meta:&#xa;        (...)&#xa;        param_path = &apos;/{entity_type}/access/{entity_id}&apos;&#xa;&#xa;    entity_id = Key(type=int)&#xa;    entity_type = Key(type=str)&#xa;&#xa;MyResource.register(api, &apos;/entities&apos;)&#xa;# Identical to:&#xa;# api.add_resource(MyResource.APIList, &apos;/entities&apos;)&#xa;# api.add_resource(MyResource.API, &apos;/entities/&lt;string:entity_type&gt;/access/&lt;int:entity_id&gt;&apos;)&#xa;#&#xa;# Without param_path, this would have led to (note the ordering):&#xa;# api.add_resource(MyResource.APIList, &apos;/entities&apos;)&#xa;# api.add_resource(MyResource.API, &apos;/entities/&lt;int:entity_id&gt;/&lt;string:entity_type&gt;&apos;)" ID="ID_878593248" CREATED="1540307378368" MODIFIED="1540307379752"/>
</node>
<node ID="ID_1985789243" CREATED="1540307392898" MODIFIED="1540307392898"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span style="color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; background-color: rgb(255, 255, 255); text-decoration: none; display: inline !important; float: none"><font color="rgb(23, 43, 77)" face="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif" size="14px">dir_path (optional, default: &lt;generated from Key fields&gt;): The path to append to the base resource to get the dir resource. This should be a string starting with '/', suitable for python .format() function, and with parameters corresponding to the name of the keys that are defined with dir_key=True.</font></span>
  </body>
</html>
</richcontent>
<node TEXT="class MyResource(CRUDResource):&#xa;     class Meta:&#xa;         dir_path = &quot;/{dir_id}/objects&quot;&#xa;         param_path = &quot;/object/{object_id}&quot;&#xa;&#xa;     dir_id = Key(type=int, dir_key=True)&#xa;     object_id = Key(type=int)&#xa;&#xa;MyResource.register(api, &apos;/resource&apos;)&#xa;# Identical to:&#xa;# api.add_resource(MyResource.APIList, &apos;/resource/&lt;integer:dir_id&gt;/objects&apos;)&#xa;# api.add_resource(MyResource.API, &apos;/resource/&lt;integer:dir_id&gt;/objects/object/&lt;integer:object_id&gt;&apos;)" ID="ID_128056805" CREATED="1540307404596" MODIFIED="1540307406464"/>
</node>
<node TEXT="validators : A dictionnary to add multi-field validators. These will be applied whenever all the parameters are accepted by the method. Unlike single-field validators, these will be applied even if parameters are not provided, so you should filter this case in your validator itself. Global validators are always applied after all single field validators are applied." ID="ID_493234528" CREATED="1540307415850" MODIFIED="1540307416899"/>
</node>
<node ID="ID_803585892" CREATED="1540306618313" MODIFIED="1540306618313"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        A list of fields (as class members), that should contain at least one Key and any amount of Data and Filters.
      </li>
    </ul>
  </body>
</html>
</richcontent>
<node TEXT="Common attributes" FOLDED="true" ID="ID_1237430886" CREATED="1540306751956" MODIFIED="1540306753045">
<node ID="ID_1181622990" CREATED="1540306769983" MODIFIED="1540306769983"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        name (implicit, required): This isn't a parameter of the constructor, this is the name of the field that is being assigned like `name = Data(...)`. It is the name that will be used for all parameters coming from user.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node FOLDED="true" ID="ID_1539497897" CREATED="1540306769983" MODIFIED="1540306769983"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        type (optional, default=str): A function used to parse arguments. Supported values are any type defined in api.lib.inputs. Examples include:
      </li>
    </ul>
  </body>
</html>
</richcontent>
<node ID="ID_699498775" CREATED="1540306769985" MODIFIED="1540306769985"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.str_norm (default, alias: str): Accepts any string, that will be stripped from trailing and leading whitespace. An empty string will be treated as None.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1607952506" CREATED="1540306769985" MODIFIED="1540306769985"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.str_raw: Accepts any string. No processing.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_512622953" CREATED="1540306769986" MODIFIED="1540306769986"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.str_path: Same as str_norm, but will allow '/' if used in a path.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1420264398" CREATED="1540306769986" MODIFIED="1540306769986"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.str_json: Accepts a json string and unpacks it.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_993215796" CREATED="1540306769986" MODIFIED="1540306769986"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.integer (alias: int): Accepts any integer. Empty string will be treated as None.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1635616712" CREATED="1540306769986" MODIFIED="1540306769986"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.floating (alias: float): Accepts any floating number. Empty string will be treated as None.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1867990297" CREATED="1540306769987" MODIFIED="1540306769987"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.boolean (alias: bool): Accepts 1, 0, true, false. Empty string will be treated as False.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1374658091" CREATED="1540306769987" MODIFIED="1540306769987"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.option: Accepts 1, 0, true, false. False will be treated as None (Special uses only - use only if you are sure of what you are doing).
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1408587010" CREATED="1540306769987" MODIFIED="1540306769987"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.datetime: Accepts any date recognized by dateutil.parser.parse
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1506454991" CREATED="1540306769987" MODIFIED="1540306769987"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        inputs.month: Accepts a single month, written in &quot;YYYY-MM&quot; format.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
<node ID="ID_869652337" CREATED="1540306769988" MODIFIED="1540306769988"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        help (optional, default=&quot;&quot;): Add a comment for the field. This comment will be put on every method identically. If you need a different comment for different methods, well, tough luck. Send me an email.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_488166737" CREATED="1540306769989" MODIFIED="1540306769989"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        dbfield (optional, default=&lt;same as name&gt;): This maps the parameter to the field &lt;dbfield&gt; in the sqlalchemy model. This can be a path using relationships (for example: `contract_id = Key(dbfield='invoice.contract_id')`), but doing so would prevent the object from being created directly (so no POST, and PUT can only perform updates). It is the user responsibility to make sure he hasn't activated POST and that PUT is update-only. A very limited number of fields use dbfields instead of dbfield. See their section for the specific behaviour of dbfields.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1001254704" CREATED="1540306769990" MODIFIED="1540306769990"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        choices (optional, default=None): This restricts accepted options to a specific list. Swagger will show it as dropdown box, and if validate is not present, a custom validation function will be generated that checks the input is present in choices.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_416448842" CREATED="1540306769991" MODIFIED="1540306769991"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        validate (optional, default=&lt;identity&gt;): This must be a function. If provided, the user parameter (as parsed by the type function above) will be given as a parameter to this function. The function must return the validated value that will be used internally, or raise a ValueError or ValidationError if the validation failed.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
<node TEXT="Example of validation function" FOLDED="true" ID="ID_1419007515" CREATED="1540306781963" MODIFIED="1540306783429">
<node TEXT="def validate_date(date):&#xa;    &quot;&quot;&quot;&#xa;    Custom date validation function (parses a date string like &quot;2017-12-31&quot;&#xa;    into a python date object.&#xa; &#xa;    Note that strptime returns a ValueError, which will be appropriately handled.&#xa;    &quot;&quot;&quot;&#xa;    return datetime.strptime(date, &quot;%Y-%m-%d&quot;).date()&#xa; &#xa;class Ressource(CRUDResource):&#xa;    date = Key(..., validate=validate_date)" ID="ID_1417906951" CREATED="1540306792842" MODIFIED="1540306794452"/>
</node>
<node TEXT="Key" ID="ID_1977899516" CREATED="1540306809932" MODIFIED="1540306811539">
<node ID="ID_1534463254" CREATED="1540306827578" MODIFIED="1540306827578"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      The most used field, this defines a field that is associated with a (part of) the primary key. In most cases, keys are part of the resource URI.
    </p>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1251759376" CREATED="1540306827579" MODIFIED="1540306838722"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      additional parameters:
    </p>
  </body>
</html>
</richcontent>
<node ID="ID_684499581" CREATED="1540306827580" MODIFIED="1540306827580"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        default (optional, default=None): Provide a default for the key, that will be only used for the GET method. This also has significant impact on the behavior of this class, as the key will no longer being part of the resource identifier.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1061853525" CREATED="1540306854906" MODIFIED="1540306854906"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span style="color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; background-color: rgb(255, 255, 255); text-decoration: none; display: inline !important; float: none"><font color="rgb(23, 43, 77)" face="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif" size="14px">When a default is provided:</font></span>
  </body>
</html>
</richcontent>
<node TEXT="Method Present Mode&#xa;PUT required query&#xa;POST no (unless dir_key) query if applicable&#xa;PATCH required query&#xa;LIST optional query&#xa;GET optional query&#xa;DELETE required query" ID="ID_97799960" CREATED="1540306913561" MODIFIED="1540306931192"/>
</node>
<node ID="ID_1625554040" CREATED="1540306865560" MODIFIED="1540306865560"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span style="color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; background-color: rgb(255, 255, 255); text-decoration: none; display: inline !important; float: none"><font color="rgb(23, 43, 77)" face="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif" size="14px">When no default is provided:</font></span>
  </body>
</html>
</richcontent>
<node TEXT="Method    Present    Mode&#xa;DELETE required path&#xa;GET required path&#xa;LIST optional query&#xa;PATCH required path&#xa;POST no (unless dir_key) path if applicable&#xa;PUT required path" ID="ID_647855705" CREATED="1540306941616" MODIFIED="1540306953151"/>
</node>
</node>
<node ID="ID_1197129799" CREATED="1540307043030" MODIFIED="1540307043030"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        hidden (optional, default=False): Makes the key an hidden field, in order to give a partial view of a table. For example, commodity = Key(hidden=True, default=&quot;gas&quot;) will make all requests act only on the gas portion of the table. This field will then apply to every method, including POST.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1860229200" CREATED="1540307043031" MODIFIED="1540307054904"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        \class Room(CRUDResource): &#160;&#160;&#160;&#160;class Meta: &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;methods = [&quot;GET&quot;, &quot;PUT&quot;, &quot;DELETE&quot;, &quot;LIST&quot;, &quot;POST&quot;] &#160; &#160;&#160;&#160;&#160;house_id = Key(type=int, dir_key=True) &#160;&#160;&#160;&#160;room_id = Key(type=int, dir_key=False) Room.register(api, '/rooms') # generates the following endpoints: # /rooms/{int:house_id} -&gt; contains LIST/POST # /rooms/{int:house_id}/{int:room_id} -&gt; contains PUT/GET/DELETE\
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
<node TEXT="Data" FOLDED="true" ID="ID_678971224" CREATED="1540307076785" MODIFIED="1540307079416">
<node ID="ID_1838783067" CREATED="1540307094150" MODIFIED="1540307094150"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      The simplest field, this creates an argument that is only used for POST, PATCH and PUT. It maps to a single field and perform updates on this field.
    </p>
  </body>
</html>
</richcontent>
</node>
<node FOLDED="true" ID="ID_336018554" CREATED="1540307094150" MODIFIED="1540307094150"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      This class accepts the following additional parameters:
    </p>
  </body>
</html>
</richcontent>
<node ID="ID_1308117107" CREATED="1540307094152" MODIFIED="1540307094152"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        default (optional, default=None): Provides a default for the object. Affects whether the argument is required.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1185303052" CREATED="1540307094152" MODIFIED="1540307094152"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        required (optional, default=&lt;depends of default&gt;: Precises whether the argument is required for both PUT and POST. Default is to be required only if no default has been provided. Note that the field is always optional for PATCH.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
<node TEXT="Method    Present    Mode&#xa;GET no -&#xa;PUT may be required data&#xa;DELETE no -&#xa;LIST no -&#xa;POST may be required data&#xa;PATCH always optional data" ID="ID_1326407435" CREATED="1540307112927" MODIFIED="1540307120786"/>
</node>
<node TEXT="NestedListData" FOLDED="true" ID="ID_1683923607" CREATED="1540307137894" MODIFIED="1540307140407">
<node ID="ID_568211026" CREATED="1540307158043" MODIFIED="1540307158043"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      A specialization of Data that maps to a collection relationship on sqlalchemy. It is used only on POST and PUT, similar to Data. It will accept as input a json corresponding to a list of argument dictionaries, each dictionary containing the arguments necessary to create a single child. Child created in this way inherits necessarily of the keys of the parent, so they must not be repeated in the json.
    </p>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_895340567" CREATED="1540307158043" MODIFIED="1540307158043"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      It accepts the following additionnal parameters:
    </p>
  </body>
</html>
</richcontent>
<node ID="ID_60375019" CREATED="1540307158044" MODIFIED="1540307158044"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        child_resource (required): The resource defining the child. This resource has the following requirements:
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
<node ID="ID_440547133" CREATED="1540307158045" MODIFIED="1540307158045"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 30px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      All keys of the parent must be repeated in the child, with dir_key=True. Additional child-specific keys must be added afterwards. Note that this means that the resource identifier of the child include the resource identifier of the parent, and that in most cases, the primary key of the child must include the primary key of the parent. See Joins in dbfield for a workaround.
    </p>
  </body>
</html>
</richcontent>
</node>
<node TEXT="class PageRessource(CRUDResource):&#xa;    class Meta:&#xa;        methods = [&apos;PUT&apos;, &apos;GET&apos;, &apos;DELETE&apos;]&#xa;    book_id = Key(dir_key=True)&#xa;    page_id = Key()&#xa;    data = Data()&#xa; &#xa;class BookResource(CRUDResource):&#xa;    class Meta:&#xa;        methods = [&apos;LIST&apos;, &apos;GET&apos;, &apos;PUT&apos;, &apos;DELETE&apos;]&#xa; &#xa;    book_id = Key()&#xa;    pages = NestedListData(PageResource)&#xa;BookResource.register(api, &apos;/books&apos;)&#xa;PageResource.register(api, &apos;/books&apos;)&#xa;# Endpoints generated:&#xa;# /books --&gt; contains LIST of BookResource&#xa;# /books/&lt;book_id&gt; --&gt; contains GET, PUT and DELETE of BookResource&#xa;# /books/&lt;book_id&gt;/&lt;page_id&gt; --&gt; contains GET, PUT and DELETE of PageResource" ID="ID_1850853594" CREATED="1540307191058" MODIFIED="1540307192742"/>
<node ID="ID_1591627631" CREATED="1540307203807" MODIFIED="1540307203807"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        default (optional, default='[]'): The default when the user doesn't provide a parameter. Should be the json encoding of a list.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1845637209" CREATED="1540307203807" MODIFIED="1540307203807"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        required (optional, default=True): Whether the argument is required.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_699379770" CREATED="1540307203808" MODIFIED="1540307203808"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        child_method (optional, choices=['PUT', 'POST', 'PUST'], default='POST'): How to consider keys of the child:
      </li>
    </ul>
  </body>
</html>
</richcontent>
<node ID="ID_1157735423" CREATED="1540307203810" MODIFIED="1540307203810"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        PUT: The keys of each child (that are not also part of the parent) must be provided.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_747430785" CREATED="1540307203810" MODIFIED="1540307203810"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        POST: The keys of each child must not be provided.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_151077517" CREATED="1540307203811" MODIFIED="1540307203811"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc">
      <li>
        PUT-POST: (default, DEPRECATED) The keys of each child can be provided, but it isn't necessary. This mode makes some assumptions about what was intended by the user, and it may lead to strange behaviours. In most cases, it is better to force an explicity key mode.<br/>
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
<node TEXT="class PageRessource(CRUDResource):&#xa;    book_id = Key(dir_key=True)&#xa;    page_id = Key()&#xa;    data = Data()&#xa; &#xa;class AuthorResource(CRUDResource):&#xa;    book_id = Key()&#xa;    author_name = Key(dir_key=True)&#xa;    data = Data()&#xa; &#xa;class BookResource(CRUDResource):&#xa;    book_id = Key()&#xa;    authors = NestedListData(AuthorResource, child_method=&quot;PUT&quot;)&#xa;    pages = NestedListData(PageResource, child_method=&quot;POST&quot;)&#xa; &#xa;# Acceptable payload for BookResource:&#xa;# authors = [{&quot;author_name&quot;: &quot;John&quot;, &quot;data&quot;: &lt;&gt;}] -- Keys must be provided for authors&#xa;# pages = [{&quot;data&quot;: &lt;&gt;}, {&quot;data&quot;: &lt;&gt;}] -- Keys must not be provided for pages" ID="ID_904935987" CREATED="1540307228151" MODIFIED="1540307228977"/>
</node>
<node TEXT="Filters" FOLDED="true" ID="ID_1929569830" CREATED="1540307277195" MODIFIED="1540307279065">
<node ID="ID_717705910" CREATED="1540307286166" MODIFIED="1540307286166"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      A collection of filters that only applies to LIST.&#160;
    </p>
  </body>
</html>
</richcontent>
</node>
<node FOLDED="true" ID="ID_1458254497" CREATED="1540307286166" MODIFIED="1540307286166"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <h4 id="Userguide-Single-FieldFilters" style="margin-top: 20px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(51, 51, 153); font-size: 14px; font-weight: 600; line-height: 1.42857142857143; letter-spacing: normal; text-transform: none; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-style: normal; text-align: start; text-indent: 0px; white-space: normal; word-spacing: 0px; text-decoration: none">
      Single-Field Filters
    </h4>
  </body>
</html>
</richcontent>
<node FOLDED="true" ID="ID_1676546275" CREATED="1540307286167" MODIFIED="1540307286167"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      These apply to a single column, defined by the argument dbfield:
    </p>
  </body>
</html>
</richcontent>
<node ID="ID_912365965" CREATED="1540307286167" MODIFIED="1540307286167"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        MappedFilter: Matches elements with equality. In most cases, it makes sense to use DataFilter instead, but this can be used when mapped to a hybrid sqla property.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1425750307" CREATED="1540307286167" MODIFIED="1540307286167"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        LowerBoundFilter: Matches elements greater that the passed parameter (included)
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_246353288" CREATED="1540307286168" MODIFIED="1540307286168"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        UpperBoundFilter: Matches elements lower that the passed parameter (included)
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1171597879" CREATED="1540307286168" MODIFIED="1540307286168"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        InListFilter: Matches elements with a 'in' (column must be a postgres array)
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
</node>
<node FOLDED="true" ID="ID_1560194485" CREATED="1540307286168" MODIFIED="1540307286168"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <h4 id="Userguide-Multi-FieldFilters" style="margin-top: 20px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(51, 51, 153); font-size: 14px; font-weight: 600; line-height: 1.42857142857143; letter-spacing: normal; text-transform: none; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-style: normal; text-align: start; text-indent: 0px; white-space: normal; word-spacing: 0px; text-decoration: none">
      Multi-Field Filters
    </h4>
  </body>
</html>
</richcontent>
<node FOLDED="true" ID="ID_885182471" CREATED="1540307286168" MODIFIED="1540307286168"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      These apply on multiple columns, that are defined by the argument dbfields:
    </p>
  </body>
</html>
</richcontent>
<node ID="ID_1838721468" CREATED="1540307286169" MODIFIED="1540307286169"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        SearchFilter: Performs a ILIKE on the set of columns, and combines the results per-column with a OR.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
</node>
</node>
</node>
</node>
<node ID="ID_1861828837" CREATED="1540306618322" MODIFIED="1540306618322"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <ul style="margin-top: 10px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px; list-style-type: disc; color: rgb(23, 43, 77); font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Fira Sans, Droid Sans, Helvetica Neue, sans-serif; font-size: 14px; font-style: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; text-decoration: none">
      <li>
        Overrides of specific functions for greater customization. See below for more details.
      </li>
    </ul>
  </body>
</html>
</richcontent>
</node>
<node TEXT="basic example" FOLDED="true" ID="ID_496203765" CREATED="1540306652205" MODIFIED="1540306660754">
<node TEXT="from lib.data.models import BeautifulEntityModel&#xa;from api.models import beautiful_response_model&#xa; &#xa;class MyRessource(CRUDResource):&#xa;    class Meta:&#xa;        # Will generate comments like &quot;Creates or updates a beautiful entity&quot; (PUT)&#xa;        description = &quot;beautiful entity&quot;&#xa;        # Must be the SQLAlchemy model&#xa;        dbmodel = BeautifulEntityModel&#xa;        # Must be the model used for replies for flask marshalling&#xa;        response_model = beautiful_response_model&#xa;        # Permission used for all endpoints. :read or :write is appended to it depending on endpoint.&#xa;        permission = &quot;beautiful&quot;&#xa; &#xa;    entity_id = Key(type=int, help=&quot;Numeric Identifier for the entity&quot;)&#xa;    name = Data(type=string, help=&quot;Name of the entity&quot;)" ID="ID_1320723854" CREATED="1540306647401" MODIFIED="1540306649626"/>
</node>
<node TEXT="reigstering the resource" ID="ID_1860597475" CREATED="1540306666586" MODIFIED="1540306669991">
<node TEXT="MyResource.register(api, &apos;/endpoint&apos;)" ID="ID_859132736" CREATED="1540306709348" MODIFIED="1540306715401"/>
<node TEXT="If you have multiple keys, these keys will be added to the path in the order they are defined in the class." ID="ID_316604989" CREATED="1540306716995" MODIFIED="1540306717783"/>
</node>
</node>
</node>
</node>
<node TEXT="DB" ID="ID_519946384" CREATED="1540280456470" MODIFIED="1540280457852">
<node TEXT="Table" ID="ID_102945764" CREATED="1540280458239" MODIFIED="1540280516902"/>
<node TEXT="Column" ID="ID_777843784" CREATED="1540280467258" MODIFIED="1540280520642">
<node TEXT="name" ID="ID_834587665" CREATED="1540280581656" MODIFIED="1540280586684"/>
<node TEXT="type" ID="ID_717917238" CREATED="1540280589087" MODIFIED="1540280591792"/>
<node TEXT="*args" ID="ID_1828342697" CREATED="1540285394480" MODIFIED="1540285403267">
<node TEXT="Constraint" ID="ID_1675039205" CREATED="1540285404241" MODIFIED="1540285408025"/>
<node TEXT="ForeignKey" ID="ID_1680638268" CREATED="1540285409155" MODIFIED="1540285414722"/>
<node TEXT="ForeignKeyConstraint" ID="ID_1163668413" CREATED="1540285434899" MODIFIED="1540285448614"/>
</node>
<node TEXT="default" ID="ID_638244568" CREATED="1540284992162" MODIFIED="1540284994545"/>
<node TEXT="nullable" ID="ID_1534063652" CREATED="1540280593272" MODIFIED="1540280596143"/>
<node TEXT="primary key" ID="ID_211985839" CREATED="1540283037667" MODIFIED="1540284603737">
<node TEXT="primary_key" ID="ID_86542598" CREATED="1540284605216" MODIFIED="1540284611783">
<node TEXT="boolean" ID="ID_471542259" CREATED="1540283050405" MODIFIED="1540283052590"/>
</node>
<node TEXT="autoincrement" ID="ID_155124133" CREATED="1540284616924" MODIFIED="1540284620657">
<node TEXT="auto" ID="ID_34601941" CREATED="1540284729265" MODIFIED="1540284731486">
<node TEXT="indicates that a single-column primary key that is of an INTEGER type with no stated client-side or python-side defaults should receive auto increment semantics automatically; all other varieties of primary key columns will not" ID="ID_728390985" CREATED="1540284906399" MODIFIED="1540284908263"/>
</node>
<node TEXT="ignore_fk" ID="ID_939260352" CREATED="1540284732061" MODIFIED="1540284742321"/>
<node TEXT="True" ID="ID_615793939" CREATED="1540284783794" MODIFIED="1540284787378">
<node TEXT="to indicate autoincrement semantics on a column that has a client-side or server-side default configured" ID="ID_1702354357" CREATED="1540284854119" MODIFIED="1540284855766"/>
</node>
<node TEXT="False" ID="ID_687846153" CREATED="1540284787614" MODIFIED="1540284790547">
<node TEXT="on a single-column primary key that has a datatype of INTEGER in order to disable auto increment semantics for that column." ID="ID_997816211" CREATED="1540284809491" MODIFIED="1540284811388"/>
</node>
</node>
</node>
<node TEXT="server_default" ID="ID_1991949637" CREATED="1540285348963" MODIFIED="1540285352649"/>
<node TEXT="key" ID="ID_533365929" CREATED="1540285050843" MODIFIED="1540285052112"/>
<node TEXT="quote" ID="ID_936917583" CREATED="1540285322212" MODIFIED="1548948805941">
<node TEXT="Force quoting of this column&#x2019;s name on or off, corresponding to True or False. When left at its default of None, the column identifier will be quoted according to whether the name is case sensitive (identifiers with at least one upper case character are treated as case sensitive), or if it&#x2019;s a reserved word. This flag is only needed to force quoting of a reserved word which is not known by the SQLAlchemy dialect" ID="ID_1121500571" CREATED="1540285324044" MODIFIED="1548948805940"/>
</node>
<node TEXT="index" FOLDED="true" ID="ID_1340115983" CREATED="1540285029154" MODIFIED="1540285036034">
<node TEXT="boolean" ID="ID_179828553" CREATED="1540285036989" MODIFIED="1540285039483"/>
<node TEXT="indicates that the column is indexed" ID="ID_575113630" CREATED="1540285080700" MODIFIED="1540285081474"/>
</node>
<node TEXT="info" FOLDED="true" ID="ID_1889125812" CREATED="1540285092133" MODIFIED="1540285093300">
<node TEXT="optional data dictionary" ID="ID_1557822940" CREATED="1540285093966" MODIFIED="1540285118194"/>
</node>
<node TEXT="unique" FOLDED="true" ID="ID_344864322" CREATED="1540285175821" MODIFIED="1540285179278">
<node TEXT="boolean" ID="ID_1841251904" CREATED="1540285180295" MODIFIED="1540285194552"/>
<node TEXT="indicates that this column contains a unique constraint" ID="ID_519303951" CREATED="1540285243028" MODIFIED="1540285244568"/>
</node>
<node TEXT="comment" FOLDED="true" ID="ID_337399784" CREATED="1540285253656" MODIFIED="1540285255191">
<node TEXT="Optional string that will render an SQL comment on table creation" ID="ID_488146634" CREATED="1540285266262" MODIFIED="1540285267930"/>
</node>
</node>
</node>
<node TEXT="CI" ID="ID_880471294" CREATED="1540393863814" MODIFIED="1540393864874">
<node TEXT="synchroniser Gitlab / Github" ID="ID_256344659" CREATED="1540393866398" MODIFIED="1540393882889" LINK="https://putaindecode.io/fr/articles/git/synchroniser-sans-effort-ses-depots-git-entre-github-gitlab-bitbucket/"/>
</node>
<node TEXT="Schema" ID="ID_1625979491" CREATED="1540452953601" MODIFIED="1540452978719">
<node TEXT="&apos;=Resource" ID="ID_1871148095" CREATED="1540452956492" MODIFIED="1540452999332"/>
<node TEXT="fields[0..n]" ID="ID_700901054" CREATED="1540453039280" MODIFIED="1540453060728">
<node TEXT="nom" ID="ID_202660934" CREATED="1540453002941" MODIFIED="1540453005192"/>
<node TEXT="type" ID="ID_1734814183" CREATED="1540453005564" MODIFIED="1540453006923"/>
<node TEXT="format" ID="ID_1058867719" CREATED="1540453019649" MODIFIED="1540453021377"/>
<node TEXT="key?" ID="ID_1617463182" CREATED="1540453487050" MODIFIED="1540453491736">
<node TEXT="primary_key: bool" ID="ID_1220914183" CREATED="1548332864110" MODIFIED="1548332910641"/>
<node TEXT="is_2_many" ID="ID_756511317" CREATED="1548334603965" MODIFIED="1548334619094">
<node TEXT="boolean" ID="ID_550819770" CREATED="1548334627732" MODIFIED="1548334631122"/>
</node>
<node TEXT="foreignRefUri" ID="ID_694237678" CREATED="1548333107244" MODIFIED="1548333134081">
<node TEXT="&apos;=foreign_key" ID="ID_1706941969" CREATED="1548332883285" MODIFIED="1548333159839"/>
<node TEXT="resolve =&gt; class" ID="ID_1875888447" CREATED="1548333068165" MODIFIED="1548333076604">
<node TEXT="ref-uri" ID="ID_648842977" CREATED="1548332922356" MODIFIED="1548332930438"/>
<node TEXT="add property to class" ID="ID_1998913772" CREATED="1548334569399" MODIFIED="1548334575327"/>
<node TEXT="cname" ID="ID_83439635" CREATED="1548332924222" MODIFIED="1548332934360"/>
</node>
</node>
</node>
<node TEXT="ordering?" ID="ID_814880172" CREATED="1540453492351" MODIFIED="1548339264703"/>
<node TEXT="static" ID="ID_1594395361" CREATED="1540456997060" MODIFIED="1540456998802">
<node TEXT="false" ID="ID_1856326740" CREATED="1540457004824" MODIFIED="1540457007667"/>
</node>
<node TEXT="class" ID="ID_1842716588" CREATED="1540457346491" MODIFIED="1540457348371">
<node TEXT="false" ID="ID_853820575" CREATED="1540457352359" MODIFIED="1540457362323"/>
<node TEXT="Meta" ID="ID_410887536" CREATED="1540457363424" MODIFIED="1540457365830"/>
</node>
<node TEXT="relationship" ID="ID_783103385" CREATED="1548331039029" MODIFIED="1548331044098">
<node TEXT="foreign_key" ID="ID_917630719" CREATED="1548331065611" MODIFIED="1548331070450">
<node TEXT="value" ID="ID_335288137" CREATED="1548331107629" MODIFIED="1548331967031"/>
</node>
<node TEXT="one2one" ID="ID_1362244730" CREATED="1548332029017" MODIFIED="1548332047116">
<node TEXT="uri" ID="ID_1818899726" CREATED="1548332047986" MODIFIED="1548332055805">
<node TEXT="we retrieve the schema" ID="ID_1212660757" CREATED="1548332100929" MODIFIED="1548332112277"/>
</node>
<node TEXT="&apos;=class" ID="ID_1127926436" CREATED="1548332117401" MODIFIED="1548334826367"/>
</node>
<node TEXT="one2many" ID="ID_990910249" CREATED="1548332056684" MODIFIED="1548332059896">
<node TEXT="uri" ID="ID_1125586419" CREATED="1548332060255" MODIFIED="1548332062929">
<node TEXT="we retrieve the schema" ID="ID_1496521806" CREATED="1548332100929" MODIFIED="1548332112277"/>
<node TEXT="&apos;=class" ID="ID_1113929775" CREATED="1548332117401" MODIFIED="1548334826367"/>
</node>
<node TEXT="details" ID="ID_801502998" CREATED="1548332071416" MODIFIED="1548332074601">
<node TEXT="type" ID="ID_706594385" CREATED="1548332074913" MODIFIED="1548332078767">
<node TEXT="array" ID="ID_1709753418" CREATED="1548332078958" MODIFIED="1548332080799"/>
</node>
<node TEXT="items" ID="ID_877520035" CREATED="1548332083714" MODIFIED="1548332085471">
<node TEXT="" ID="ID_197117844" CREATED="1548332085763" MODIFIED="1548332085763"/>
</node>
</node>
</node>
<node TEXT="type" ID="ID_1582935917" CREATED="1548331114717" MODIFIED="1548331118558">
<node TEXT="&apos;= targetSchemaUri" ID="ID_129632993" CREATED="1548331118887" MODIFIED="1548331957372"/>
</node>
<node TEXT=".resolve()" ID="ID_1853344356" CREATED="1548331976285" MODIFIED="1548332012967"/>
<node TEXT=".validate()" ID="ID_198878723" CREATED="1548332019025" MODIFIED="1548332023512"/>
</node>
</node>
<node TEXT="methods[0..n]" ID="ID_997349481" CREATED="1540453101940" MODIFIED="1540453175523">
<node TEXT="arguments" ID="ID_927220074" CREATED="1540453120447" MODIFIED="1540453123459">
<node TEXT="input / output" ID="ID_368995156" CREATED="1540453155877" MODIFIED="1540453159899"/>
</node>
<node TEXT="return" ID="ID_688294708" CREATED="1540453123636" MODIFIED="1540453153029"/>
<node TEXT="visibility" ID="ID_1912638682" CREATED="1540456846771" MODIFIED="1540456849992">
<node TEXT="public/private/protected" ID="ID_1271706435" CREATED="1540453090700" MODIFIED="1540453101517"/>
</node>
<node TEXT="static" ID="ID_246257354" CREATED="1540453180130" MODIFIED="1540456880661">
<node TEXT="false" ID="ID_578635930" CREATED="1540457011885" MODIFIED="1540457014605"/>
</node>
<node TEXT="class" ID="ID_927163351" CREATED="1540457175503" MODIFIED="1540457177030">
<node TEXT="false" ID="ID_208930297" CREATED="1540457177487" MODIFIED="1540457179185"/>
<node TEXT="A class method receives the class as implicit first argument, just like an instance method receives the instance" ID="ID_812926762" CREATED="1540457335361" MODIFIED="1540457336285"/>
</node>
</node>
<node TEXT="relationships[0..n]" ID="ID_1697401061" CREATED="1540457473161" MODIFIED="1540457485111">
<node TEXT="links via foreign keys" ID="ID_794016322" CREATED="1540457485969" MODIFIED="1540457497316">
<node TEXT="$reference" ID="ID_140892862" CREATED="1540457501904" MODIFIED="1540457510079"/>
</node>
</node>
<node TEXT="api endpoints" ID="ID_1544191524" CREATED="1541422392342" MODIFIED="1541422401341">
<node TEXT="Meta" ID="ID_651820852" CREATED="1540453197618" MODIFIED="1540453200787">
<node TEXT="description" ID="ID_938602684" CREATED="1540453201475" MODIFIED="1540453203733"/>
<node TEXT="permission" ID="ID_1943493833" CREATED="1540453260267" MODIFIED="1540453276277"/>
<node TEXT="db_model" ID="ID_1805809790" CREATED="1540453267507" MODIFIED="1540453287877"/>
<node TEXT="response_model" ID="ID_767327528" CREATED="1540453288682" MODIFIED="1540453293067"/>
<node TEXT="response_model_list" ID="ID_65303361" CREATED="1540453295962" MODIFIED="1540453302853"/>
<node TEXT="methods" ID="ID_1491402788" CREATED="1540453305397" MODIFIED="1540453309322">
<node TEXT="GET" ID="ID_1728513442" CREATED="1540453328675" MODIFIED="1540453330506"/>
<node TEXT="LIST" ID="ID_1625225901" CREATED="1540453330827" MODIFIED="1540453332157"/>
<node TEXT="PATCH" ID="ID_583248208" CREATED="1540453332669" MODIFIED="1540453336407"/>
<node TEXT="PUT" ID="ID_1794265906" CREATED="1540453337105" MODIFIED="1540453338548"/>
<node TEXT="DELETE" ID="ID_1124397510" CREATED="1540453339146" MODIFIED="1540453340656"/>
</node>
<node TEXT="validators" ID="ID_1861153299" CREATED="1540453309581" MODIFIED="1540453312133"/>
</node>
<node TEXT="api calls test" ID="ID_784068641" CREATED="1541410180067" MODIFIED="1541410287038">
<node TEXT="params" ID="ID_1066033400" CREATED="1541410189876" MODIFIED="1541410194194"/>
<node TEXT="data" ID="ID_1424860756" CREATED="1541410194418" MODIFIED="1541410254778"/>
<node TEXT="files" ID="ID_1767343805" CREATED="1541410309120" MODIFIED="1541410317044"/>
<node TEXT="api_key" ID="ID_1456527962" CREATED="1541411841018" MODIFIED="1561108280379">
<arrowlink SHAPE="CUBIC_CURVE" COLOR="#000000" WIDTH="2" TRANSPARENCY="200" FONT_SIZE="9" FONT_FAMILY="SansSerif" DESTINATION="ID_1249048406" STARTINCLINATION="40;0;" ENDINCLINATION="40;0;" STARTARROW="NONE" ENDARROW="DEFAULT"/>
</node>
<node TEXT="user" ID="ID_1087519349" CREATED="1541421985081" MODIFIED="1561108280379">
<arrowlink SHAPE="CUBIC_CURVE" COLOR="#000000" WIDTH="2" TRANSPARENCY="200" FONT_SIZE="9" FONT_FAMILY="SansSerif" DESTINATION="ID_1249048406" STARTINCLINATION="40;0;" ENDINCLINATION="40;0;" STARTARROW="NONE" ENDARROW="DEFAULT"/>
</node>
<node TEXT="headers" ID="ID_1249048406" CREATED="1541421958925" MODIFIED="1541421963435"/>
<node TEXT="expected" ID="ID_596976525" CREATED="1541410271183" MODIFIED="1541410273788">
<node TEXT="json" ID="ID_837800548" CREATED="1541410274441" MODIFIED="1541410275781"/>
<node TEXT="code" ID="ID_959484282" CREATED="1541410276219" MODIFIED="1541410277746"/>
</node>
</node>
</node>
<node TEXT="Serialisation" FOLDED="true" ID="ID_1518469208" CREATED="1540453649178" MODIFIED="1540453670404">
<node TEXT="logical" ID="ID_691631159" CREATED="1540453672890" MODIFIED="1540453686326"/>
<node TEXT="to_physical" ID="ID_1941109015" CREATED="1540453689079" MODIFIED="1540453704745"/>
<node TEXT="to_json" ID="ID_231877066" CREATED="1540453705086" MODIFIED="1540453711029"/>
<node TEXT="to_url ??" ID="ID_1082611466" CREATED="1540453712308" MODIFIED="1540453730102"/>
<node TEXT="to_human??" ID="ID_1136045665" CREATED="1540453730527" MODIFIED="1540453738614"/>
<node TEXT="to_plural?" ID="ID_151493033" CREATED="1540453739160" MODIFIED="1540456118853"/>
<node TEXT="to_lang_fr" ID="ID_1135972548" CREATED="1540453766919" MODIFIED="1540456085975">
<node TEXT="plural" ID="ID_1551413620" CREATED="1540456101847" MODIFIED="1540456108805"/>
</node>
</node>
<node TEXT="Data" ID="ID_836620225" CREATED="1540456413318" MODIFIED="1540456415192">
<node TEXT="Logical" ID="ID_42411811" CREATED="1540456415539" MODIFIED="1540456417499"/>
<node TEXT="Physical" ID="ID_1793888199" CREATED="1540456417679" MODIFIED="1540456421499"/>
<node TEXT="Class" ID="ID_1188060435" CREATED="1540456421923" MODIFIED="1540456423668"/>
<node TEXT="Api" ID="ID_608318160" CREATED="1540456423962" MODIFIED="1540456425936">
<node TEXT="route" ID="ID_1596493789" CREATED="1540456592143" MODIFIED="1540456593563"/>
<node TEXT="methods" ID="ID_619971632" CREATED="1540453305397" MODIFIED="1540453309322">
<node TEXT="GET" ID="ID_484088187" CREATED="1540453328675" MODIFIED="1540453330506">
<node TEXT="permission" ID="ID_282014421" CREATED="1540456637354" MODIFIED="1540456641291"/>
</node>
<node TEXT="LIST" ID="ID_1678856070" CREATED="1540453330827" MODIFIED="1540453332157"/>
<node TEXT="PATCH" ID="ID_1700317010" CREATED="1540453332669" MODIFIED="1540453336407"/>
<node TEXT="PUT" ID="ID_1161980506" CREATED="1540453337105" MODIFIED="1540453338548"/>
<node TEXT="DELETE" ID="ID_955796169" CREATED="1540453339146" MODIFIED="1540453340656"/>
</node>
<node TEXT="validation" ID="ID_306489253" CREATED="1541520875862" MODIFIED="1541520880299">
<node TEXT="flask-expects" ID="ID_962729254" CREATED="1541520886925" MODIFIED="1541520896012" LINK="https://pypi.org/project/flask-expects-json/"/>
</node>
</node>
</node>
</node>
</node>
<node TEXT="DATA MODELS" POSITION="right" ID="ID_1591279921" CREATED="1554974607633" MODIFIED="1554974612241">
<edge COLOR="#ff00ff"/>
<node TEXT="Series" ID="ID_1029483465" CREATED="1554974614488" MODIFIED="1554974623419">
<node TEXT="meta" ID="ID_861511117" CREATED="1554974744661" MODIFIED="1554974746583"/>
<node TEXT="values" ID="ID_1589623724" CREATED="1554974737522" MODIFIED="1554974740335"/>
<node TEXT="index" ID="ID_484166815" CREATED="1554974741874" MODIFIED="1554974743863"/>
</node>
<node TEXT="TimeSeries" ID="ID_1405064928" CREATED="1554974623731" MODIFIED="1554974627785">
<node TEXT="meta" ID="ID_413595947" CREATED="1554974754162" MODIFIED="1554974756246"/>
<node TEXT="values" ID="ID_1678272479" CREATED="1554974756674" MODIFIED="1554974759296"/>
<node TEXT="datetimeindex" ID="ID_770961757" CREATED="1554974768180" MODIFIED="1554974773905"/>
</node>
<node TEXT="DataFrame" ID="ID_990958277" CREATED="1554974628834" MODIFIED="1554974632075">
<node TEXT="keys" ID="ID_1444083990" CREATED="1554974662503" MODIFIED="1554974667003">
<node TEXT="[[keys_level1], [keys_level2], ...]" ID="ID_458586015" CREATED="1554974672718" MODIFIED="1554974705876"/>
<node TEXT="must be in meta" ID="ID_1414825508" CREATED="1554974707646" MODIFIED="1554974722168"/>
</node>
<node TEXT="[Meta]" ID="ID_422729783" CREATED="1554974633275" MODIFIED="1554974658783"/>
<node TEXT="[TimeSeries]" ID="ID_1420464565" CREATED="1554974641109" MODIFIED="1554974648821"/>
</node>
</node>
<node TEXT="Generator" POSITION="right" ID="ID_1388181555" CREATED="1561404622909" MODIFIED="1561404764179">
<edge COLOR="#7c0000"/>
<attribute NAME="directory" VALUE=""/>
<node TEXT="PackageGenerator" ID="ID_1300532592" CREATED="1561404627637" MODIFIED="1561404672363"/>
<node TEXT="ComponentGenerator" ID="ID_292001849" CREATED="1561404673046" MODIFIED="1561404678354"/>
</node>
<node TEXT="generation" POSITION="right" ID="ID_915794275" CREATED="1561405583691" MODIFIED="1561405591297">
<edge COLOR="#00007c"/>
<node TEXT="serialize_package" ID="ID_65580352" CREATED="1561405592009" MODIFIED="1561405599623"/>
<node TEXT="serialize_component" ID="ID_1909687590" CREATED="1561405600035" MODIFIED="1561405608534"/>
<node TEXT="generate_package_info(package, directory)" ID="ID_1296080591" CREATED="1561405615181" MODIFIED="1561405694606"/>
<node TEXT="generate_component_info(component, directory)" ID="ID_951842371" CREATED="1561405647760" MODIFIED="1561405704741"/>
</node>
<node TEXT="my way of life" POSITION="right" ID="ID_572201847" CREATED="1563955561178" MODIFIED="1563955574083">
<edge COLOR="#7c007c"/>
<node TEXT="follow me" ID="ID_888965922" CREATED="1563955575966" MODIFIED="1563955579241">
<node TEXT="tags des categories d interet" ID="ID_775025134" CREATED="1563955580105" MODIFIED="1563955591203"/>
<node TEXT="channels" ID="ID_178192339" CREATED="1563955592294" MODIFIED="1563955596797">
<node TEXT="blog" ID="ID_652295486" CREATED="1563955597475" MODIFIED="1563955599724"/>
<node TEXT="email" ID="ID_633405225" CREATED="1563955599934" MODIFIED="1563955601366"/>
<node TEXT="rss" ID="ID_1528842176" CREATED="1563955601663" MODIFIED="1563955602728"/>
<node TEXT="notifications android" ID="ID_1338686950" CREATED="1563955603447" MODIFIED="1563955615268"/>
<node TEXT="facebook" ID="ID_829993575" CREATED="1563955625947" MODIFIED="1563955627895"/>
<node TEXT="instagram" ID="ID_640238906" CREATED="1563955628227" MODIFIED="1563955635760"/>
<node TEXT="twitter" ID="ID_1151889224" CREATED="1563955639970" MODIFIED="1563955642314"/>
</node>
<node TEXT="infos" ID="ID_1160787347" CREATED="1563955650457" MODIFIED="1563955654157">
<node TEXT="signe" ID="ID_954247432" CREATED="1563955654968" MODIFIED="1563955656877">
<node TEXT="date de naissance" ID="ID_1055802896" CREATED="1563955657625" MODIFIED="1563955662677"/>
<node TEXT="heure de naissance" ID="ID_1725948552" CREATED="1563955662845" MODIFIED="1563955665771"/>
</node>
<node TEXT="longitute/latitude de naissance" ID="ID_1851070665" CREATED="1563955667987" MODIFIED="1563955679517"/>
</node>
<node TEXT="sexe" ID="ID_487065280" CREATED="1563955739820" MODIFIED="1563955743373">
<node TEXT="M" ID="ID_47423165" CREATED="1563955744144" MODIFIED="1563955745246"/>
<node TEXT="F" ID="ID_501773792" CREATED="1563955745768" MODIFIED="1563955746503"/>
<node TEXT="other" ID="ID_59981610" CREATED="1563955748547" MODIFIED="1563955753655"/>
</node>
<node TEXT="orientation" ID="ID_1511152562" CREATED="1563955755829" MODIFIED="1563955759445"/>
<node TEXT="industry" ID="ID_1619372443" CREATED="1563955785640" MODIFIED="1563955789442"/>
</node>
</node>
<node TEXT="my big bang" POSITION="right" ID="ID_424989270" CREATED="1563956163493" MODIFIED="1563956172492">
<edge COLOR="#007c7c"/>
<node TEXT="video tagging" ID="ID_1095654468" CREATED="1563956173286" MODIFIED="1563956185195">
<node TEXT="characters" ID="ID_1725395145" CREATED="1563956271495" MODIFIED="1563956274676"/>
<node TEXT="objects" ID="ID_1019623663" CREATED="1563956275074" MODIFIED="1563956280817"/>
<node TEXT="animals" ID="ID_942718957" CREATED="1563956286877" MODIFIED="1563956289185"/>
<node TEXT="places" ID="ID_1395640222" CREATED="1563959969851" MODIFIED="1563959975243"/>
<node TEXT="events" ID="ID_1778236918" CREATED="1563959975452" MODIFIED="1563959978655"/>
<node TEXT="music" ID="ID_476904693" CREATED="1563959994101" MODIFIED="1563959997874"/>
</node>
<node TEXT="video formatting" ID="ID_262336442" CREATED="1563956185698" MODIFIED="1563956191677">
<node TEXT="regarder le format kinemaster" ID="ID_427790519" CREATED="1563956195927" MODIFIED="1563956208095"/>
</node>
<node TEXT="scenario editing" ID="ID_1063222652" CREATED="1563956248920" MODIFIED="1563956257666"/>
</node>
<node TEXT="django serializer" POSITION="right" ID="ID_1554832255" CREATED="1563956330501" MODIFIED="1563956339386">
<edge COLOR="#7c7c00"/>
</node>
<node TEXT="sqlalchemy" POSITION="right" ID="ID_785535791" CREATED="1563956349183" MODIFIED="1563956537168">
<edge COLOR="#ff0000"/>
<node TEXT="??" ID="ID_1200320418" CREATED="1563958694399" MODIFIED="1563958696548"/>
</node>
<node TEXT="kivi ?" POSITION="right" ID="ID_1695412190" CREATED="1564166662601" MODIFIED="1564166666600">
<edge COLOR="#ff00ff"/>
</node>
<node TEXT="OpenAPI / JsonSchema" POSITION="right" ID="ID_37039276" CREATED="1563971904624" MODIFIED="1563971912952">
<edge COLOR="#0000ff"/>
<node TEXT="openapi-and-json-schema-divergence-part-1" ID="ID_529443736" CREATED="1563971928701" MODIFIED="1563971952902" LINK="https://apisyouwonthate.com/blog/openapi-and-json-schema-divergence-part-1">
<node ID="ID_840590910" CREATED="1563972590320" MODIFIED="1563972590320"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    OpenAPI
  </body>
</html>
</richcontent>
<node TEXT="API documentations tools" ID="ID_44235864" CREATED="1563972600430" MODIFIED="1563972665899" LINK="https://blog.apisyouwonthate.com/turning-contracts-into-beautiful-documentation-deac7013af18"/>
<node TEXT="fancy SDK generators" ID="ID_88877551" CREATED="1563972666684" MODIFIED="1563972673513"/>
<node ID="ID_534012641" CREATED="1563972741687" MODIFIED="1563972741687"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    API-specific functionality
  </body>
</html>
</richcontent>
</node>
<node TEXT="focus on keeping this static, for strictly typed languages, where properties should be 1 type and 1 type only" ID="ID_137075916" CREATED="1563972715646" MODIFIED="1563972719555"/>
</node>
<node TEXT="Json Schema" ID="ID_1117671143" CREATED="1563972694770" MODIFIED="1563972713381">
<node ID="ID_583101939" CREATED="1563972831527" MODIFIED="1563972831527"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    very flexible data modeling with the same sort of validation vocabulary as OpenAPI, but for more flexible data sets
  </body>
</html>
</richcontent>
</node>
<node ID="ID_431957177" CREATED="1563972856543" MODIFIED="1563972856543" LINK="https://blog.apisyouwonthate.com/getting-started-with-json-hyper-schema-184775b91f"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    by using more advanced vocabularies like <a href="https://blog.apisyouwonthate.com/getting-started-with-json-hyper-schema-184775b91f">JSON Hyper-Schema</a> it can model a fully RESTful API and its hypermedia controls (HATEOAS)
  </body>
</html>
</richcontent>
</node>
</node>
</node>
<node TEXT="solving-openapi-and-json-schema-divergence" ID="ID_944208025" CREATED="1563971939107" MODIFIED="1563971960379" LINK="https://apisyouwonthate.com/blog/solving-openapi-and-json-schema-divergence"/>
<node TEXT="Comprendre-la-specification-OpenAPI-Swagger-et-apprendre-a-utiliser-Swagger-Editor" ID="ID_719135629" CREATED="1563975286619" MODIFIED="1563975298565" LINK="https://www.developpez.com/actu/178434/Comprendre-la-specification-OpenAPI-Swagger-et-apprendre-a-utiliser-Swagger-Editor-par-Hinault-Romaric/"/>
<node TEXT="https://openapi-map.apihandyman.io/?version=3.0" ID="ID_1123363982" CREATED="1563978435029" MODIFIED="1563978435029" LINK="https://openapi-map.apihandyman.io/?version=3.0"/>
</node>
<node TEXT="conversion openapi-jsonschema" POSITION="right" ID="ID_1191746743" CREATED="1564125683324" MODIFIED="1564126355928">
<edge COLOR="#00ff00"/>
<node ID="ID_9288971" CREATED="1564126356751" MODIFIED="1564126356751" LINK="https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#fixed-fields-20)"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    converts OpenAPI 3.0 Schema Object to JSON Schema Draft 4<br/>* deletes `nullable` and adds `&quot;null&quot;` to `type` array if `nullable` is `true`<br/>* supports deep structures with nested `allOf`s etc.<br/>* removes [OpenAPI specific<br/>properties](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#fixed-fields-20)<br/>such as `discriminator`, `deprecated` etc. unless specified otherwise<br/>* optionally supports `patternProperties` with `x-patternProperties` in the<br/>Schema Object
  </body>
</html>
</richcontent>
</node>
<node TEXT="" ID="ID_794296227" CREATED="1564126360927" MODIFIED="1564126360927"/>
</node>
<node TEXT="MWOL" POSITION="right" ID="ID_686516418" CREATED="1564171277072" MODIFIED="1564296759550">
<edge COLOR="#00ffff"/>
<node TEXT="python manage.py createsuperuser" ID="ID_1032093772" CREATED="1564171280461" MODIFIED="1564171282413"/>
<node TEXT="animaux totems" FOLDED="true" ID="ID_973651245" CREATED="1564262680670" MODIFIED="1564296759549" LINK="https://www.espritsciencemetaphysiques.com/voici-un-guide-complet-sur-les-animaux-totems.html">
<node TEXT="tigre du bengale" ID="ID_1566748715" CREATED="1564262684427" MODIFIED="1564262688017"/>
<node TEXT="ours" ID="ID_579388913" CREATED="1564262812163" MODIFIED="1564262814160"/>
<node TEXT="Le totem du Loup" ID="ID_724257480" CREATED="1564262776723" MODIFIED="1564262776723"/>
<node TEXT="Le totem du Corbeau ou de la Corneille" ID="ID_148608924" CREATED="1564262776723" MODIFIED="1564262776723"/>
<node TEXT="Le totem de la Chouette ou Hibou" ID="ID_74937604" CREATED="1564262776726" MODIFIED="1564262776726"/>
<node TEXT="Le Faucon / L aigle" ID="ID_233422735" CREATED="1564262776726" MODIFIED="1564262855135"/>
<node TEXT="Le Serpent" ID="ID_862598239" CREATED="1564262776727" MODIFIED="1564262776727"/>
<node TEXT="Le Renard" ID="ID_1548483977" CREATED="1564262776727" MODIFIED="1564262776727"/>
<node TEXT="Le cheval" ID="ID_847403183" CREATED="1564262887684" MODIFIED="1564262891961"/>
<node TEXT="La baleine" ID="ID_555643424" CREATED="1564262892290" MODIFIED="1564262897462"/>
<node TEXT="Le Fourmilier" ID="ID_1796379017" CREATED="1564262897849" MODIFIED="1564262905990"/>
<node TEXT="L oppossum" ID="ID_1314881162" CREATED="1564262906211" MODIFIED="1564262910801"/>
<node TEXT="cerf / biche" ID="ID_651535801" CREATED="1564262863665" MODIFIED="1564262868947"/>
<node TEXT="papillon" ID="ID_293036712" CREATED="1564262922955" MODIFIED="1564262926646"/>
<node TEXT="libellule" ID="ID_1796753493" CREATED="1564262926889" MODIFIED="1564262978384"/>
<node TEXT="Le Lion" ID="ID_1262921363" CREATED="1564262962381" MODIFIED="1564262965285"/>
<node TEXT="Araignee" ID="ID_1506153936" CREATED="1564262965593" MODIFIED="1564262970681"/>
<node TEXT="chat" ID="ID_1385909462" CREATED="1564262970922" MODIFIED="1564262974829"/>
<node TEXT="coyotte" ID="ID_1880080032" CREATED="1564263006057" MODIFIED="1564263007752"/>
<node TEXT="crapaud" ID="ID_435757012" CREATED="1564263008016" MODIFIED="1564263012660"/>
<node TEXT="singe" ID="ID_1141880223" CREATED="1564263013970" MODIFIED="1564263015206"/>
<node TEXT="tortue" ID="ID_1661178251" CREATED="1564263030832" MODIFIED="1564263033575"/>
<node TEXT="colibri" ID="ID_118625042" CREATED="1564263033829" MODIFIED="1564263046999"/>
<node TEXT="belier/mouton" ID="ID_549519852" CREATED="1564263066099" MODIFIED="1564263070366"/>
<node TEXT="panda" ID="ID_1841675550" CREATED="1564263083059" MODIFIED="1564263085041"/>
<node TEXT="koala" ID="ID_332510215" CREATED="1564263085322" MODIFIED="1564263086682"/>
<node TEXT="loutre" ID="ID_443466205" CREATED="1564263090900" MODIFIED="1564263093076"/>
</node>
</node>
<node TEXT="create a plugin" POSITION="right" ID="ID_920999928" CREATED="1564381929367" MODIFIED="1564381934752">
<edge COLOR="#7c0000"/>
<node TEXT="add directory to /scripts/classpath" ID="ID_1019846347" CREATED="1564381936611" MODIFIED="1564381967852"/>
<node TEXT="install jython" ID="ID_1977335032" CREATED="1564381975051" MODIFIED="1564381979073">
<node TEXT="https://www.freeplane.org/wiki/index.php/Scripting:_Other_languages" ID="ID_169581073" CREATED="1564381969718" MODIFIED="1564381969718" LINK="https://www.freeplane.org/wiki/index.php/Scripting:_Other_languages"/>
</node>
</node>
<node TEXT="serveur local" POSITION="right" ID="ID_1585107801" CREATED="1564385155613" MODIFIED="1564385164670">
<edge COLOR="#00007c"/>
<node TEXT="tourne en demon" ID="ID_1371646889" CREATED="1564385170612" MODIFIED="1564385174571"/>
<node TEXT="watch des directory" ID="ID_46220685" CREATED="1564385174879" MODIFIED="1564385178875">
<node TEXT="cree un projet par directory avec du contenu media" ID="ID_643330318" CREATED="1564385181327" MODIFIED="1564385203698">
<node TEXT="photo" ID="ID_30073454" CREATED="1564385218477" MODIFIED="1564385223466"/>
<node TEXT="video" ID="ID_831018000" CREATED="1564385223813" MODIFIED="1564385225210"/>
<node TEXT="pdf" ID="ID_578982414" CREATED="1564385225511" MODIFIED="1564385239316"/>
<node TEXT="ebook" ID="ID_401758672" CREATED="1564385264721" MODIFIED="1564385266961"/>
<node TEXT="mm" ID="ID_1837985066" CREATED="1564385244539" MODIFIED="1564385246347"/>
</node>
</node>
<node TEXT="cut" ID="ID_1538955414" CREATED="1564388169359" MODIFIED="1564388171396"/>
<node TEXT="crop" ID="ID_1527468895" CREATED="1564388224935" MODIFIED="1564388230706"/>
<node TEXT="resize" ID="ID_558832326" CREATED="1564388231049" MODIFIED="1564388234313"/>
</node>
<node TEXT="serveur distant" POSITION="right" ID="ID_2626297" CREATED="1564385165280" MODIFIED="1564385169011">
<edge COLOR="#007c00"/>
<node TEXT="backup" ID="ID_1152942437" CREATED="1564385280748" MODIFIED="1564385301666"/>
<node TEXT="resample" ID="ID_389582592" CREATED="1564385400004" MODIFIED="1564385442065"/>
<node TEXT="categories" ID="ID_73055643" CREATED="1564385451481" MODIFIED="1564385465378"/>
<node TEXT="tags" ID="ID_1528127038" CREATED="1564388158924" MODIFIED="1564388161314"/>
</node>
<node TEXT="faire un versioned_literal" POSITION="right" ID="ID_539418123" CREATED="1564385319651" MODIFIED="1564385335485">
<edge COLOR="#7c007c"/>
</node>
<node TEXT="faire un xml serialzer" POSITION="right" ID="ID_1831693086" CREATED="1564421464131" MODIFIED="1564421473111">
<edge COLOR="#007c7c"/>
<node TEXT="attributes" ID="ID_30381627" CREATED="1564421473965" MODIFIED="1564421476266">
<node TEXT="all properties literals" ID="ID_736639958" CREATED="1564421476627" MODIFIED="1564421484680">
<node TEXT="for sequence &quot;,&quot;.join" ID="ID_1615310650" CREATED="1564421496669" MODIFIED="1564421542050"/>
</node>
</node>
<node TEXT="elements" ID="ID_561582676" CREATED="1564421485765" MODIFIED="1564421488568">
<node TEXT="all objects" ID="ID_1573802970" CREATED="1564421488831" MODIFIED="1564421492362"/>
</node>
</node>
<node TEXT="wrapper vers sql" POSITION="right" ID="ID_1592814547" CREATED="1564433090306" MODIFIED="1564433121080">
<edge COLOR="#7c7c00"/>
<node TEXT="load_all" ID="ID_75599229" CREATED="1564433122351" MODIFIED="1564433126707"/>
<node TEXT="load_query" ID="ID_1707583262" CREATED="1564433127402" MODIFIED="1564433139976"/>
</node>
<node TEXT="faire un systeme de views" POSITION="right" ID="ID_738821474" CREATED="1564477001126" MODIFIED="1564477008612">
<edge COLOR="#ff0000"/>
<node TEXT="un modele" ID="ID_1610864096" CREATED="1564477009595" MODIFIED="1564477012767">
<node TEXT="une vue html" ID="ID_661897945" CREATED="1564477013480" MODIFIED="1564477046721"/>
<node TEXT="une vue html liste" ID="ID_98504444" CREATED="1564477018901" MODIFIED="1564477062003"/>
<node TEXT="une vue mindmap" ID="ID_721529825" CREATED="1564477073860" MODIFIED="1564477078039"/>
</node>
</node>
<node TEXT="packages" POSITION="right" ID="ID_192486155" CREATED="1564487663116" MODIFIED="1564487667280">
<edge COLOR="#0000ff"/>
<node TEXT="https://github.com/asifpy/django-crudbuilder" ID="ID_610311349" CREATED="1564487668370" MODIFIED="1564487668370" LINK="https://github.com/asifpy/django-crudbuilder"/>
<node TEXT="DRF" ID="ID_1284868518" CREATED="1564487719189" MODIFIED="1564487725448" LINK="https://www.django-rest-framework.org/tutorial/quickstart/"/>
<node TEXT="" ID="ID_44914922" CREATED="1564489164138" MODIFIED="1564489164138">
<node TEXT="{&quot;(96,\&quot;2019-07-30 12:05:30.44304+00\&quot;,\&quot;{\&quot;\&quot;value\&quot;\&quot;: 0.641374282058931}\&quot;)&quot;,&quot;(94,\&quot;2019-07-30 11:47:11.391083+00\&quot;,\&quot;{\&quot;\&quot;value\&quot;\&quot;: 0.641374282058931}\&quot;)&quot;,&quot;(59,\&quot;2019-07-29 16:03:18.650746+00\&quot;,\&quot;{\&quot;\&quot;value\&quot;\&quot;: 0.318618274500223}\&quot;)&quot;,&quot;(,\&quot;2019-07-18 08:37:17.190726+00\&quot;,)&quot;}" ID="ID_1321823899" CREATED="1564489166780" MODIFIED="1564489166780"/>
</node>
<node TEXT="https://pypi.org/project/awscli/" ID="ID_1270731063" CREATED="1564511186455" MODIFIED="1564511186455" LINK="https://pypi.org/project/awscli/"/>
</node>
<node TEXT="ZAPPA!!!!" POSITION="right" ID="ID_1441834435" CREATED="1564510839581" MODIFIED="1564510847292">
<edge COLOR="#00ff00"/>
<node TEXT="combo zappa/docker/aws" ID="ID_430444258" CREATED="1564510852413" MODIFIED="1564510864595"/>
<node TEXT="https://andytwoods.com/python-zappa-django-cookiecutter-via-pycharm.html" ID="ID_851396297" CREATED="1564511329236" MODIFIED="1564511329236" LINK="https://andytwoods.com/python-zappa-django-cookiecutter-via-pycharm.html"/>
</node>
<node TEXT="cookiecutter" POSITION="right" ID="ID_1444085435" CREATED="1564510848298" MODIFIED="1564510878822">
<edge COLOR="#ff00ff"/>
<node TEXT="django-app" ID="ID_1882474314" CREATED="1564510943465" MODIFIED="1564510947558">
<node TEXT="django" ID="ID_575474031" CREATED="1564510879581" MODIFIED="1564510884899"/>
<node TEXT="django-cms" ID="ID_230428889" CREATED="1564510885647" MODIFIED="1564510889131">
<node TEXT="django-categories" ID="ID_1832235017" CREATED="1564510916940" MODIFIED="1564510922589"/>
</node>
<node TEXT="django-rest" ID="ID_1226517534" CREATED="1564510889546" MODIFIED="1564510898981"/>
<node TEXT="zappa" ID="ID_1448579719" CREATED="1564510899971" MODIFIED="1564510905608">
<node TEXT="awscli" ID="ID_207485353" CREATED="1564511194290" MODIFIED="1564511197200"/>
<node TEXT="boto" ID="ID_1390985964" CREATED="1564511197700" MODIFIED="1564511198714"/>
</node>
</node>
<node TEXT="django-plugin" ID="ID_1024608933" CREATED="1564510953604" MODIFIED="1564510957352">
<node TEXT="&lt;plugin&gt;_settings.json" ID="ID_1819933616" CREATED="1564510981815" MODIFIED="1564511001541"/>
</node>
</node>
<node TEXT="faire une methode from_mm" POSITION="right" ID="ID_979087916" CREATED="1564516810723" MODIFIED="1564516822000">
<edge COLOR="#00ffff"/>
<node TEXT="qui construit un object ProtocolBased sur une mindmap" ID="ID_1661462138" CREATED="1564516824100" MODIFIED="1564516844543"/>
</node>
<node TEXT="bots" POSITION="right" ID="ID_1186227802" CREATED="1564726720958" MODIFIED="1564726723495">
<edge COLOR="#7c0000"/>
<node TEXT="astro" ID="ID_1591019866" CREATED="1564726723684" MODIFIED="1564726727299">
<node TEXT="kin (maya)" ID="ID_517130859" CREATED="1564726763897" MODIFIED="1564726773397"/>
<node TEXT="matchs amoureux" ID="ID_335335613" CREATED="1564726783269" MODIFIED="1564726787027"/>
</node>
<node TEXT="genetique" ID="ID_659752593" CREATED="1564726727882" MODIFIED="1564726735335">
<node TEXT="indices" ID="ID_387671748" CREATED="1564726736222" MODIFIED="1564726742346"/>
</node>
<node TEXT="robot de cul" ID="ID_902004703" CREATED="1564726806003" MODIFIED="1564726819427"/>
<node TEXT="robot coach" ID="ID_1129412649" CREATED="1564726819816" MODIFIED="1564726825170"/>
</node>
<node TEXT="RULE" POSITION="left" ID="ID_1472485660" CREATED="1561806490260" MODIFIED="1561806493063">
<edge COLOR="#007c00"/>
<node TEXT="class attributes" ID="ID_1289278252" CREATED="1561806493745" MODIFIED="1561806502171">
<node TEXT="at object definition" ID="ID_1993754869" CREATED="1561806503291" MODIFIED="1561806534734"/>
<node TEXT="__ATTR__" ID="ID_1912369174" CREATED="1561806536478" MODIFIED="1561806549916">
<node TEXT="in python" ID="ID_734961414" CREATED="1561806551379" MODIFIED="1561806555910"/>
</node>
</node>
<node TEXT="instances attributes" ID="ID_1436460263" CREATED="1561806509112" MODIFIED="1561806517825">
<node TEXT="in properties" ID="ID_312070482" CREATED="1561806519384" MODIFIED="1561806521696"/>
</node>
<node TEXT="$" ID="ID_1972541974" CREATED="1561806568757" MODIFIED="1561806572716">
<node TEXT="comment or uri" ID="ID_510430760" CREATED="1561806574031" MODIFIED="1561806582289"/>
</node>
</node>
</node>
</map>

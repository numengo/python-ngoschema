<map version="freeplane 1.7.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="NUMENGO" FOLDED="false" ID="ID_1508363761" CREATED="1560152088771" MODIFIED="1560848402492" STYLE="oval">
<font SIZE="18"/>
<hook NAME="MapStyle">
    <properties show_icon_for_attributes="true" fit_to_viewport="false" edgeColorConfiguration="#808080ff,#ff0000ff,#0000ffff,#00ff00ff,#ff00ffff,#00ffffff,#7c0000ff,#00007cff,#007c00ff,#7c007cff,#007c7cff,#7c7c00ff"/>

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
<hook NAME="AutomaticEdgeColor" COUNTER="74" RULE="ON_BRANCH_CREATION"/>
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
<node TEXT="projects" FOLDED="true" POSITION="right" ID="ID_1259015571" CREATED="1548839942180" MODIFIED="1560848530967">
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
<node TEXT="Ideas for NUMENGO" POSITION="right" ID="ID_1951444762" CREATED="1539956303171" MODIFIED="1540280422287">
<edge COLOR="#7c0000"/>
<node TEXT="API" FOLDED="true" ID="ID_1848375593" CREATED="1540280423111" MODIFIED="1540280427059">
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
<node TEXT="DB" FOLDED="true" ID="ID_519946384" CREATED="1540280456470" MODIFIED="1540280457852">
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
<node TEXT="CI" FOLDED="true" ID="ID_880471294" CREATED="1540393863814" MODIFIED="1540393864874">
<node TEXT="synchroniser Gitlab / Github" ID="ID_256344659" CREATED="1540393866398" MODIFIED="1540393882889" LINK="https://putaindecode.io/fr/articles/git/synchroniser-sans-effort-ses-depots-git-entre-github-gitlab-bitbucket/"/>
</node>
<node TEXT="Schema" FOLDED="true" ID="ID_1625979491" CREATED="1540452953601" MODIFIED="1540452978719">
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
<node TEXT="DATA MODELS" FOLDED="true" POSITION="right" ID="ID_1591279921" CREATED="1554974607633" MODIFIED="1554974612241">
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
<node TEXT="my way of life" FOLDED="true" POSITION="right" ID="ID_572201847" CREATED="1563955561178" MODIFIED="1563955574083">
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
<node TEXT="my big bang" FOLDED="true" POSITION="right" ID="ID_424989270" CREATED="1563956163493" MODIFIED="1563956172492">
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
<node TEXT="OpenAPI / JsonSchema" FOLDED="true" POSITION="right" ID="ID_37039276" CREATED="1563971904624" MODIFIED="1563971912952">
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
<node TEXT="serveur local" FOLDED="true" POSITION="right" ID="ID_1585107801" CREATED="1564385155613" MODIFIED="1564385164670">
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
<node TEXT="packages" FOLDED="true" POSITION="right" ID="ID_192486155" CREATED="1564487663116" MODIFIED="1564487667280">
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
<node TEXT="cookiecutter" FOLDED="true" POSITION="right" ID="ID_1444085435" CREATED="1564510848298" MODIFIED="1564510878822">
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
<node TEXT="faire une methode from_mm" FOLDED="true" POSITION="right" ID="ID_979087916" CREATED="1564516810723" MODIFIED="1564516822000">
<edge COLOR="#00ffff"/>
<node TEXT="qui construit un object ProtocolBased sur une mindmap" ID="ID_1661462138" CREATED="1564516824100" MODIFIED="1564516844543"/>
<node TEXT="class" ID="ID_1004057364" CREATED="1566642966627" MODIFIED="1566642975493"/>
<node TEXT="enum" ID="ID_954608509" CREATED="1566642982506" MODIFIED="1566642984468">
<node TEXT="name" ID="ID_1153098785" CREATED="1566643348684" MODIFIED="1566643350764">
<node TEXT="value" ID="ID_680878570" CREATED="1566643352168" MODIFIED="1566643354020"/>
</node>
<node TEXT="" ID="ID_373774116" CREATED="1566643357180" MODIFIED="1566643357180"/>
</node>
<node TEXT="function" ID="ID_716978733" CREATED="1566642984824" MODIFIED="1566642987167">
<node TEXT="description" ID="ID_615243926" CREATED="1566643242485" MODIFIED="1566643246488"/>
<node TEXT="arguments" ID="ID_3008360" CREATED="1566642988349" MODIFIED="1566642993024">
<node TEXT="name" ID="ID_1571149869" CREATED="1566643029386" MODIFIED="1566643033480">
<node TEXT="type" ID="ID_729664315" CREATED="1566643063093" MODIFIED="1566643066761"/>
<node TEXT="const?" ID="ID_1680949191" CREATED="1566643067113" MODIFIED="1566643071548"/>
<node TEXT="description" ID="ID_1317792454" CREATED="1566643113608" MODIFIED="1566643227881"/>
</node>
</node>
<node TEXT="return" ID="ID_1575743143" CREATED="1566642993368" MODIFIED="1566642996564"/>
<node TEXT="exceptions" ID="ID_1263126367" CREATED="1566643049317" MODIFIED="1566643056599"/>
</node>
</node>
<node TEXT="bots" FOLDED="true" POSITION="right" ID="ID_1186227802" CREATED="1564726720958" MODIFIED="1564726723495">
<edge COLOR="#7c0000"/>
<node TEXT="astro" ID="ID_1591019866" CREATED="1564726723684" MODIFIED="1564726727299">
<node TEXT="kin (maya)" ID="ID_517130859" CREATED="1564726763897" MODIFIED="1564726773397"/>
<node TEXT="matchs amoureux" ID="ID_335335613" CREATED="1564726783269" MODIFIED="1564726787027"/>
</node>
<node TEXT="genetique" ID="ID_659752593" CREATED="1564726727882" MODIFIED="1564726735335">
<node TEXT="macros" ID="ID_387671748" CREATED="1564726736222" MODIFIED="1564764592302"/>
</node>
<node TEXT="robot de cul" ID="ID_902004703" CREATED="1564726806003" MODIFIED="1564726819427"/>
<node TEXT="robot coach" ID="ID_1129412649" CREATED="1564726819816" MODIFIED="1564726825170"/>
<node TEXT="robot lover" ID="ID_1162345526" CREATED="1564764574277" MODIFIED="1564764581567"/>
<node TEXT="robot dealer" ID="ID_1756266274" CREATED="1564764596584" MODIFIED="1564764601149"/>
<node TEXT="robot speeddating" ID="ID_1839733561" CREATED="1564875077331" MODIFIED="1564875083489">
<node TEXT="profil" ID="ID_910808897" CREATED="1564875090703" MODIFIED="1564875094425"/>
<node TEXT="astro match localis&#xe9;" ID="ID_651277816" CREATED="1564875279344" MODIFIED="1564875286832"/>
</node>
</node>
<node TEXT="equivalence class / openapi" FOLDED="true" POSITION="right" ID="ID_102038829" CREATED="1564764693231" MODIFIED="1566637731976">
<edge COLOR="#00007c"/>
<node TEXT="package" ID="ID_29017800" CREATED="1564764739846" MODIFIED="1564764774830">
<node TEXT="resources" ID="ID_1685027403" CREATED="1564764735722" MODIFIED="1564764737914"/>
</node>
<node TEXT="class" ID="ID_1438787812" CREATED="1564764775979" MODIFIED="1564764778122">
<node TEXT="definitions" ID="ID_1993700699" CREATED="1564764778340" MODIFIED="1564764781431"/>
<node TEXT="class attributes" ID="ID_1216287507" CREATED="1565097857863" MODIFIED="1565097868732">
<node TEXT="" ID="ID_1649015786" CREATED="1565097859934" MODIFIED="1565097859934"/>
</node>
<node TEXT="instance attributes" ID="ID_1000767340" CREATED="1565097868989" MODIFIED="1565097872185">
<node TEXT="table columns" ID="ID_864950325" CREATED="1565097872708" MODIFIED="1565097877651"/>
<node TEXT="json keys" ID="ID_1886989598" CREATED="1565097878675" MODIFIED="1565097884952"/>
</node>
</node>
<node TEXT="function/method" ID="ID_774087017" CREATED="1564764718970" MODIFIED="1564764728784">
<node TEXT="method" ID="ID_995786321" CREATED="1564764731425" MODIFIED="1564764734520"/>
<node TEXT="arguments" ID="ID_1425936395" CREATED="1564764801638" MODIFIED="1564764804446">
<node TEXT="args" ID="ID_273624999" CREATED="1564764701743" MODIFIED="1564764705460">
<node TEXT="path / regex" ID="ID_766544053" CREATED="1564764705758" MODIFIED="1564764855198"/>
</node>
<node TEXT="kwargs" ID="ID_564386393" CREATED="1564764708433" MODIFIED="1564764711760">
<node TEXT="query" ID="ID_1798036584" CREATED="1564764711966" MODIFIED="1564764860375"/>
<node TEXT="data" ID="ID_1153793142" CREATED="1564764883573" MODIFIED="1564764884970"/>
</node>
</node>
</node>
<node TEXT="return" ID="ID_1470105374" CREATED="1564765308508" MODIFIED="1564765310891">
<node TEXT="response[0]" ID="ID_1598737289" CREATED="1564765216890" MODIFIED="1564765298727"/>
</node>
<node TEXT="exceptions" ID="ID_269864520" CREATED="1564765316313" MODIFIED="1564765318154">
<node TEXT="response[1:]" ID="ID_1689686151" CREATED="1564765318894" MODIFIED="1564765326724"/>
</node>
<node TEXT="enums" ID="ID_1969528906" CREATED="1566536603547" MODIFIED="1566536607599">
<node TEXT="name" ID="ID_1527777925" CREATED="1566536608833" MODIFIED="1566536622536">
<node TEXT="value" ID="ID_124466766" CREATED="1566536622887" MODIFIED="1566536626225"/>
</node>
<node TEXT="description" ID="ID_1874733503" CREATED="1566536648851" MODIFIED="1566536652968"/>
</node>
</node>
<node TEXT="Paris Immobilier - bague" POSITION="right" ID="ID_721651791" CREATED="1566536728495" MODIFIED="1566536750590">
<edge COLOR="#7c007c"/>
<node TEXT="emails" ID="ID_359067108" CREATED="1566536754202" MODIFIED="1566536757234">
<node TEXT="email 1" FOLDED="true" ID="ID_11538047" CREATED="1565186919808" MODIFIED="1566536762737">
<node TEXT="Bonsoir" ID="ID_1866627969" CREATED="1565186926335" MODIFIED="1565192112562"/>
<node TEXT="Comme expliqu&#xe9; a Mme HELIN de vive voix, je continue de chercher la bague qui a disparu lors de la visite de Mme DIABY." ID="ID_950278232" CREATED="1565192112827" MODIFIED="1565194141592"/>
<node TEXT="Si je ne l ai pas retrouv&#xe9; d ici lundi, chez moi ou ma boite aux lettres, je n aurais alors plus aucun doute que Mme DIABY l a prise lors de sa visite pour prendre des photos de l appartement pour la relocation." ID="ID_1402850136" CREATED="1565192224789" MODIFIED="1565192323724"/>
<node TEXT="J ai decouvert la disparition immediatement apres son passage, je lui ai ecrit le lendemain apres avoir vraiment bien cherch&#xe9; dans l appartement." ID="ID_1715507817" CREATED="1565192325498" MODIFIED="1565192385783"/>
<node TEXT="Apres un mois de poursuite des recherches, je lui ai fait part de ma quasi-certitude de sa culpabilit&#xe9;. Neanmoins, je veux recuperer cette bague, et je lui ai donn&#xe9; la possibilit&#xe9; de r&#xe9;gler ca sans y meler la police ou son employeur." ID="ID_565601449" CREATED="1565192390911" MODIFIED="1565192577582"/>
<node TEXT="Pourtant bien avertie, elle ne sera donc pas etonn&#xe9;e de la suite que vont prendre les choses." ID="ID_1568742875" CREATED="1565192577844" MODIFIED="1565192646823"/>
<node TEXT="Si lundi je n ai toujours pas retrouv&#xe9; ma bague en pliant toutes mes affaires (et promis je vais bien chercher, surtout dans la boite aux lettres), j aurais cette certitude absolue, et vous, Mme HELIN, pourrez l avoir aussi, que Mme DIABY est une voleuse." ID="ID_108783586" CREATED="1565192647374" MODIFIED="1565194166329"/>
<node TEXT="J irai donc porter plainte pour commencer les procedures, et j imagine que dans les circonstances du vol, impliquant des gerants des 2 societes, votre soci&#xe9;t&#xe9; dans l ensemble sera concern&#xe9;e." ID="ID_1681673819" CREATED="1565192746354" MODIFIED="1565192964379"/>
<node TEXT="Si Mme DIABY est effectivement une voleuse, il est alors gravissime qu elle puisse avoir acces a des cl&#xe9;s d appartement dans le cadre de ses fonctions, surtout de la mani&#xe9;re dont sont conserv&#xe9;es vos cl&#xe9;s (heureusement que je me suis pas ferm&#xe9; dehors en pensant que vous en aviez un double comme c &#xe9;tait convenu a  l etat des lieux)." ID="ID_1597562748" CREATED="1565192982338" MODIFIED="1565194192508"/>
<node TEXT="A mon retour de voyage, si j apprends qu elle exerce toujours dans votre etablissement, je m occuperai si bien de votre r&#xe9;putation que vous n aurez pas qu a vous reconvertir en relais-colis, ce qui est a peu pres le seul service que vous rendiez correctement vu de ma fen&#xea;tre. A propos des frais d agence, vous pourrez constatez sur le bail que vous avez voi" ID="ID_363279409" CREATED="1565192966553" MODIFIED="1565194258147"/>
<node TEXT="Pour ce qui est de Mme DIABY, elle pourra se tourner vers une autre carriere car si j apprends qu elle poursuit dans l immobilier, j appellerai ces futurs employeurs pour les avertir de la situation." ID="ID_1085878554" CREATED="1565193190248" MODIFIED="1565193264970"/>
<node TEXT="Notez bien Je suis consultant informaticien et influenceur a mes heures perdues, et qu on ne parle pas d une simple review sur google." ID="ID_653809978" CREATED="1565193238846" MODIFIED="1565193769108"/>
<node TEXT="Si je retrouve ma bague et que mme DIABY n y est pour rien, je vous promets qu elle recevra un bouquet de fleurs a la hauteur de la gravit&#xe9; des accusations que je fonde. Si je la retrouve dans la boite aux lettres, j en resterai la en esperant que la seule le&#xe7;on servira." ID="ID_1632777619" CREATED="1565193807983" MODIFIED="1565194066488"/>
</node>
</node>
</node>
<node TEXT="mindmap" POSITION="right" ID="ID_118952607" CREATED="1566536832237" MODIFIED="1566536836732">
<edge COLOR="#7c7c00"/>
<node TEXT="google keep" ID="ID_499243330" CREATED="1566536836862" MODIFIED="1566536842100">
<node TEXT="import" ID="ID_48186450" CREATED="1566536874343" MODIFIED="1566536878458">
<node TEXT="keepnote as mindmap" ID="ID_45554339" CREATED="1566536890164" MODIFIED="1566565290297"/>
</node>
<node TEXT="export" ID="ID_1937652261" CREATED="1566536879241" MODIFIED="1566536881375">
<node TEXT="branch as keepnote" ID="ID_1839228103" CREATED="1566565274927" MODIFIED="1566565284329"/>
</node>
<node TEXT="gkeepapi" ID="ID_1265530141" CREATED="1566536882399" MODIFIED="1566536885029"/>
</node>
<node TEXT="cms" ID="ID_169815097" CREATED="1566536843092" MODIFIED="1566536846712"/>
</node>
<node TEXT="keys / passwords" POSITION="right" ID="ID_1481717863" CREATED="1566552020609" MODIFIED="1566552025770">
<edge COLOR="#ff0000"/>
<node TEXT="https://pypi.org/project/keyring/" ID="ID_533441071" CREATED="1566552026567" MODIFIED="1566552026567" LINK="https://pypi.org/project/keyring/"/>
<node TEXT="for windows" ID="ID_1530530477" CREATED="1566552055594" MODIFIED="1566552063100">
<node TEXT="https://docs.microsoft.com/en-us/windows/uwp/security/credential-locker" ID="ID_913905557" CREATED="1566552064083" MODIFIED="1566552064083" LINK="https://docs.microsoft.com/en-us/windows/uwp/security/credential-locker"/>
</node>
</node>
<node TEXT="canonicalName" POSITION="right" ID="ID_781175154" CREATED="1566844189107" MODIFIED="1566844194815">
<edge COLOR="#00ff00"/>
<node TEXT="_cname" ID="ID_430540243" CREATED="1566844195671" MODIFIED="1566844204881">
<node TEXT="read-only" ID="ID_1410153187" CREATED="1566844270107" MODIFIED="1566844274117"/>
<node TEXT="parent._cname + &quot;.&quot; + name" ID="ID_142907289" CREATED="1566844205104" MODIFIED="1566844391465"/>
</node>
<node TEXT="canonicalName" ID="ID_793458808" CREATED="1566844277393" MODIFIED="1566844281407">
<node TEXT="read / write" ID="ID_902360320" CREATED="1566844283346" MODIFIED="1566844296359"/>
<node TEXT="default" ID="ID_1289022403" CREATED="1566844296639" MODIFIED="1566844299460">
<node TEXT="cname" ID="ID_1273327386" CREATED="1566844299599" MODIFIED="1566844300829"/>
</node>
</node>
<node TEXT="strategy" ID="ID_1454066318" CREATED="1566845047657" MODIFIED="1566845053147">
<node TEXT="change in name or parent.cname" ID="ID_82236773" CREATED="1566845053754" MODIFIED="1566845077794">
<node TEXT="update_cname" ID="ID_1213926388" CREATED="1566845082516" MODIFIED="1566845087612"/>
</node>
</node>
<node TEXT="RETHINK" ID="ID_133918755" CREATED="1566845256873" MODIFIED="1566845266112">
<node TEXT="canonicalName should be read-only" ID="ID_1485822429" CREATED="1566845266430" MODIFIED="1566845283248"/>
<node TEXT="actually, what if we want to initialize an object out of all his parents???" ID="ID_1529251611" CREATED="1566849971195" MODIFIED="1566850008972"/>
</node>
<node TEXT="dont have a registry by cname" ID="ID_1928714946" CREATED="1566853167626" MODIFIED="1566853182576">
<node TEXT="have a registry by id" ID="ID_30609881" CREATED="1566853183695" MODIFIED="1566853199374">
<node TEXT="never unregister cname" ID="ID_495427101" CREATED="1566853200771" MODIFIED="1566853212013"/>
</node>
</node>
</node>
<node TEXT="FMI" POSITION="right" ID="ID_1951743253" CREATED="1567430836197" MODIFIED="1567430837374">
<edge COLOR="#7c0000"/>
<node TEXT="FMI_for_ModelExchange_and_CoSimulation_v2.0.pdf" ID="ID_778669261" CREATED="1567508132223" MODIFIED="1567508132227" LINK="../../../Documents/DEV%20RESOURCES/FMI_for_ModelExchange_and_CoSimulation_v2.0/FMI_for_ModelExchange_and_CoSimulation_v2.0.pdf"/>
<node TEXT="Status" ID="ID_130391162" CREATED="1567430684522" MODIFIED="1567430841660">
<node TEXT="Ok" ID="ID_1757163797" CREATED="1567430688121" MODIFIED="1567430690697"/>
<node TEXT="Warning" FOLDED="true" ID="ID_1652849015" CREATED="1567430691487" MODIFIED="1567430693046">
<node TEXT="things are not quite right, but the computation can continue. Function &#x201c;logger&#x201d; was called in the model (see below) and it is expected that this function has shown the prepared information message to the user." ID="ID_174121592" CREATED="1567430722046" MODIFIED="1567430722046"/>
</node>
<node TEXT="Discard" FOLDED="true" ID="ID_1300822466" CREATED="1567430693507" MODIFIED="1567430695337">
<node TEXT="For &#x201c;model exchange&#x201d;: It is recommended to perform a smaller step size and evaluate the model equations again, for example because an iterative solver in the model did not converge or because a function is outside of its domain (for example sqrt(&lt;negative number&gt;)). If this is not possible, the simulation has to be terminated. For &#x201c;co-simulation&#x201d;: fmifmi2Discard is returned also if the slave is not able to return the required status information. The master has to decide if the simulation run can be continued. In both cases, function &#x201c;logger&#x201d; was called in the FMU (see below) and it is expected that this function has shown the prepared information message to the user if the FMU was called in debug mode (loggingOn = fmifmi2True). Otherwise, &#x201c;logger&#x201d; should not show a message." ID="ID_165010925" CREATED="1567430741288" MODIFIED="1567430741288"/>
</node>
<node TEXT="Error" FOLDED="true" ID="ID_1134453689" CREATED="1567430695745" MODIFIED="1567430697138">
<node TEXT="the FMU encountered an error. The simulation cannot be continued with this FMU instance" ID="ID_1514151389" CREATED="1567430754866" MODIFIED="1567430759189"/>
<node TEXT="Further processing is possible after this call; especially other FMU instances are not affected. Function &#x201c;logger&#x201d; was called in the FMU (see below) and it is expected that this function has shown the prepared information message to the user." ID="ID_1749556387" CREATED="1567430767495" MODIFIED="1567430769324"/>
</node>
<node TEXT="Fatal" FOLDED="true" ID="ID_175775287" CREATED="1567430697531" MODIFIED="1567430699620">
<node TEXT="the model computations are irreparably corrupted for all FMU instances. [For example, due to a run-time exception such as access violation or integer division by zero during the execution of an fmi function]. Function &#x201c;logger&#x201d; was called in the FMU (see below) and it is expected that this function has shown the prepared information message to the user. It is not possible to call any other function for any of the FMU instances." ID="ID_821663402" CREATED="1567430795054" MODIFIED="1567430796591"/>
</node>
<node TEXT="Pending" FOLDED="true" ID="ID_1876690108" CREATED="1567430699933" MODIFIED="1567430702352">
<node TEXT="is returned only from the co-simulation interface, if the slave executes the function in an asynchronous way. That means the slave starts to compute but returns immediately. The master has to call fmifmi2GetStatus(..., fmifmi2DoStepStatus) to determine, if the slave has finished the computation. Can be returned only by fmifmi2DoStep and by fmifmi2GetStatus" ID="ID_954267912" CREATED="1567430818987" MODIFIED="1567430818987"/>
</node>
</node>
<node TEXT="Instanciate" ID="ID_656026141" CREATED="1567430851404" MODIFIED="1567430855198">
<node TEXT="instanceName" ID="ID_935008803" CREATED="1567430857820" MODIFIED="1567430861544"/>
<node TEXT="type" ID="ID_438489634" CREATED="1567430861960" MODIFIED="1567430867021"/>
<node TEXT="GUID" ID="ID_1768022449" CREATED="1567430867445" MODIFIED="1567430869990"/>
<node TEXT="ResourceLocation" ID="ID_945370623" CREATED="1567430870857" MODIFIED="1567430878265"/>
<node TEXT="functions" ID="ID_1728433733" CREATED="1567430881068" MODIFIED="1567430888864"/>
<node TEXT="visible" ID="ID_1245300955" CREATED="1567430892852" MODIFIED="1567430895313"/>
<node TEXT="loggingOn" ID="ID_661134879" CREATED="1567430897410" MODIFIED="1567430902540"/>
</node>
<node TEXT="setupExperiment" ID="ID_6569394" CREATED="1567430945058" MODIFIED="1567430950208">
<node TEXT="component" ID="ID_1447930805" CREATED="1567430951907" MODIFIED="1567430953745"/>
<node TEXT="bool toleranceDefined" ID="ID_1657523750" CREATED="1567430954477" MODIFIED="1567430965421"/>
<node TEXT="tolerance" ID="ID_347351053" CREATED="1567430966028" MODIFIED="1567430968364"/>
<node TEXT="startTime" ID="ID_1558868593" CREATED="1567430968651" MODIFIED="1567430973537"/>
<node TEXT="stopTimeDefined" ID="ID_1018038838" CREATED="1567430973777" MODIFIED="1567430978287"/>
<node TEXT="stopTime" ID="ID_442779757" CREATED="1567430978551" MODIFIED="1567430980628"/>
</node>
<node TEXT="enterInitializationMode" ID="ID_988307172" CREATED="1567431079098" MODIFIED="1567431085789">
<node TEXT="Informs the FMU to enter Initialization Mode. Before calling this function, all variables with attribute &lt;ScalarVariable initial = &quot;exact&quot; or &quot;approx&quot;&gt; can be set with the &#x201c;fmifmi2SetXXX&#x201d; functions (the ScalarVariable attributes are defined in the Model Description File, see section 2.2.7). Setting other variables is not allowed. Furthermore, fmifmi2SetupExperiment must be called at least once before calling fmifmi2EnterInitializationMode, in order that startTime is defined." ID="ID_462211129" CREATED="1567431095825" MODIFIED="1567431095825"/>
</node>
<node TEXT="exitInitializationMode" ID="ID_1866114088" CREATED="1567431050432" MODIFIED="1567431059031">
<node TEXT="Informs the FMU to exit Initialization Mode. For fmuType = fmifmi2ModelExchange, this function switches off all initialization equations and the FMU enters implicitely Event Mode, that is all continuous-time and active discrete-time equations are available" ID="ID_1987023957" CREATED="1567431070775" MODIFIED="1567431070775"/>
</node>
<node TEXT="getState" ID="ID_732312517" CREATED="1567431175443" MODIFIED="1567431182475"/>
<node TEXT="setState" ID="ID_1977240750" CREATED="1567431183990" MODIFIED="1567431208302"/>
<node TEXT="freeState" ID="ID_434213934" CREATED="1567431209133" MODIFIED="1567431212125"/>
<node TEXT="state" ID="ID_1883053387" CREATED="1567431242297" MODIFIED="1567431247739">
<node TEXT="get" ID="ID_1423082360" CREATED="1567431248688" MODIFIED="1567431250400"/>
<node TEXT="set" ID="ID_190592360" CREATED="1567431250652" MODIFIED="1567431251662"/>
<node TEXT="free" ID="ID_1729394934" CREATED="1567431251999" MODIFIED="1567431253123"/>
<node TEXT="serializedSize" ID="ID_1884391610" CREATED="1567431255030" MODIFIED="1567431271287"/>
<node TEXT="serialized" ID="ID_453261529" CREATED="1567431358540" MODIFIED="1567431365531">
<node TEXT="serialize()" ID="ID_921004065" CREATED="1567431259509" MODIFIED="1567431264731"/>
</node>
<node TEXT="deserialize" ID="ID_1292268899" CREATED="1567431288569" MODIFIED="1567431300755">
<node TEXT="deserialize &apos;serialized&apos;of lenght size" ID="ID_1431956595" CREATED="1567431309735" MODIFIED="1567431356068"/>
</node>
</node>
<node TEXT="getEventIndicators" ID="ID_1288180260" CREATED="1567450770714" MODIFIED="1567450781886"/>
<node TEXT="modelDescription" ID="ID_1669465192" CREATED="1567431878231" MODIFIED="1567431886367">
<node TEXT="version" ID="ID_1767097512" CREATED="1567431887964" MODIFIED="1567431889867"/>
<node TEXT="name" ID="ID_1626351822" CREATED="1567431890145" MODIFIED="1567431891963"/>
<node TEXT="guid" ID="ID_1377922306" CREATED="1567431892322" MODIFIED="1567431893237"/>
<node TEXT="description" ID="ID_1729682273" CREATED="1567431894063" MODIFIED="1567431897258"/>
<node TEXT="author" ID="ID_212291921" CREATED="1567431897592" MODIFIED="1567431898667"/>
<node TEXT="fmiVersion" ID="ID_668234779" CREATED="1567431899106" MODIFIED="1567431906353"/>
<node TEXT="copyright" ID="ID_994956678" CREATED="1567431907732" MODIFIED="1567431911203"/>
<node TEXT="license" ID="ID_1150236309" CREATED="1567431911569" MODIFIED="1567431914534"/>
<node TEXT="generationTool" ID="ID_1108372101" CREATED="1567431914991" MODIFIED="1567431920584"/>
<node TEXT="generation" ID="ID_1752569889" CREATED="1567431921401" MODIFIED="1567431926141">
<node TEXT="tool" ID="ID_451814590" CREATED="1567431926970" MODIFIED="1567431928084"/>
<node TEXT="datetime" ID="ID_392094534" CREATED="1567431928447" MODIFIED="1567431932103"/>
<node TEXT="variableNamingConvention" ID="ID_867131790" CREATED="1567431932659" MODIFIED="1567431948801"/>
</node>
<node TEXT="eventIndicators" ID="ID_517969518" CREATED="1567431953994" MODIFIED="1567431958340"/>
</node>
<node TEXT="logCategory" ID="ID_1611818671" CREATED="1567432083463" MODIFIED="1567432091214">
<node TEXT="Events" ID="ID_1413824975" CREATED="1567432091518" MODIFIED="1567432194560"/>
<node TEXT="SingularLinearSystems" ID="ID_661201561" CREATED="1567432093962" MODIFIED="1567432189504"/>
<node TEXT="NonLinearSystems" ID="ID_266193797" CREATED="1567432102422" MODIFIED="1567432108388"/>
<node TEXT="DynamicStateSelection" ID="ID_1540811097" CREATED="1567432109355" MODIFIED="1567432158356"/>
<node TEXT="StatusDiscard" ID="ID_1047570730" CREATED="1567432159130" MODIFIED="1567432167434"/>
<node TEXT="StatusFatal" ID="ID_578379529" CREATED="1567432167685" MODIFIED="1567508253190"/>
<node TEXT="StatusPending" ID="ID_1463866163" CREATED="1567432172298" MODIFIED="1567432181185"/>
<node TEXT="All" ID="ID_935272348" CREATED="1567432175645" MODIFIED="1567432177311"/>
</node>
<node TEXT="scalarVariable" ID="ID_264847500" CREATED="1567432229244" MODIFIED="1567432236718">
<node TEXT="name" ID="ID_559334263" CREATED="1567432236980" MODIFIED="1567432237784"/>
<node TEXT="valueReference" ID="ID_1258135552" CREATED="1567432238950" MODIFIED="1567432241399"/>
<node TEXT="description" ID="ID_1378584776" CREATED="1567432241489" MODIFIED="1567432255917"/>
<node TEXT="causality" ID="ID_1684181291" CREATED="1567432257597" MODIFIED="1567432262189">
<node TEXT="parameter" ID="ID_221534144" CREATED="1567432268126" MODIFIED="1567432272848"/>
<node TEXT="calculatedParameter" ID="ID_349324992" CREATED="1567432273216" MODIFIED="1567432280596"/>
<node TEXT="input" ID="ID_1031090719" CREATED="1567432280816" MODIFIED="1567432282701"/>
<node TEXT="output" ID="ID_1699914736" CREATED="1567432283163" MODIFIED="1567432284339"/>
<node TEXT="local" ID="ID_1645127497" CREATED="1567432284836" MODIFIED="1567432287041"/>
<node TEXT="independant" ID="ID_1202891977" CREATED="1567432287302" MODIFIED="1567432290639"/>
</node>
<node TEXT="variability" ID="ID_1939083366" CREATED="1567432291962" MODIFIED="1567432295246">
<node TEXT="constant" ID="ID_331174326" CREATED="1567432295599" MODIFIED="1567432300277"/>
<node TEXT="fixed" ID="ID_86662974" CREATED="1567432300554" MODIFIED="1567432310408"/>
<node TEXT="tunable" ID="ID_1710665972" CREATED="1567432311713" MODIFIED="1567432313580"/>
<node TEXT="discrete" ID="ID_1615262978" CREATED="1567432313980" MODIFIED="1567432315878"/>
<node TEXT="continuous" ID="ID_1684842570" CREATED="1567432316156" MODIFIED="1567432318725"/>
</node>
<node TEXT="initial" ID="ID_775539238" CREATED="1567432322052" MODIFIED="1567432324056">
<node TEXT="exact" ID="ID_1424755517" CREATED="1567432324397" MODIFIED="1567432326217"/>
<node TEXT="approx" ID="ID_512039114" CREATED="1567432326444" MODIFIED="1567432328508"/>
<node TEXT="calculated" ID="ID_1412979433" CREATED="1567432328865" MODIFIED="1567432332317"/>
</node>
</node>
<node TEXT="modelStructure" ID="ID_267313741" CREATED="1567435820076" MODIFIED="1567435824798">
<node TEXT="Outputs" ID="ID_1302619541" CREATED="1567435825388" MODIFIED="1567435827493"/>
<node TEXT="Derivatives" ID="ID_1955912123" CREATED="1567435827831" MODIFIED="1567435830680"/>
<node TEXT="InitialUnkowns" ID="ID_628856999" CREATED="1567435831324" MODIFIED="1567435842944"/>
<node TEXT="Unknown" ID="ID_1743857369" CREATED="1567435861118" MODIFIED="1567435877108">
<node TEXT="dependencies" ID="ID_1259007687" CREATED="1567435877372" MODIFIED="1567435881418"/>
<node TEXT="dependenciesKind" ID="ID_188358409" CREATED="1567435881796" MODIFIED="1567435891153">
<node TEXT="dependent" ID="ID_1956606432" CREATED="1567435893442" MODIFIED="1567435912575">
<node TEXT="no particular structure, &#x210e;(..,&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56;,..)" ID="ID_1160795450" CREATED="1567507444391" MODIFIED="1567507444391"/>
</node>
<node TEXT="constant" ID="ID_1382378377" CREATED="1567435912951" MODIFIED="1567435914623">
<node TEXT="Only for Real unknowns" ID="ID_176428603" CREATED="1567507500681" MODIFIED="1567507500681"/>
<node TEXT="constant factor" ID="ID_166377470" CREATED="1567507543902" MODIFIED="1567507543902"/>
</node>
<node TEXT="fixed" ID="ID_695314186" CREATED="1567435914819" MODIFIED="1567435916491">
<node TEXT="fixed factor, &#xd835;&#xdc5d;&#x2219;&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56; where &#xd835;&#xdc5d; is an expression that is evaluated before fmifmi2ExitInitializationMode is called." ID="ID_1828290145" CREATED="1567507576116" MODIFIED="1567507576116"/>
</node>
<node TEXT="tunable" ID="ID_697520236" CREATED="1567435916853" MODIFIED="1567435918532">
<node TEXT="tunable factor, &#xd835;&#xdc5d;&#x2219;&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56; where &#xd835;&#xdc5d; is an expression that is evaluated before fmifmi2ExitInitializationMode is called and in Event Mode due to an external event (ModelExchange) or at a Communication Point (CoSimulation)" ID="ID_1825650321" CREATED="1567507589592" MODIFIED="1567507589592"/>
</node>
<node TEXT="discrete" ID="ID_1611872220" CREATED="1567435918880" MODIFIED="1567435921440">
<node TEXT="discrete factor, &#xd835;&#xdc51;&#x2219;&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56; where &#xd835;&#xdc51; is an expression that is evaluated before fmifmi2ExitInitializationMode is called and in Event Mode due to an external or internal event or at a Communication Point (CoSimulation)." ID="ID_1307153158" CREATED="1567507684362" MODIFIED="1567507686118"/>
</node>
</node>
</node>
</node>
<node TEXT="mode" ID="ID_95593780" CREATED="1567450159400" MODIFIED="1567450163922">
<node TEXT="initialization" ID="ID_579629071" CREATED="1567450164131" MODIFIED="1567450169406">
<node TEXT="This mode is used to compute at the start time &#xd835;&#xdc61;0 initial values for continuous-time states, &#xd835;&#xdc31;&#xd835;&#xdc50;(&#xd835;&#xdc61;0), and for the previous (internal) discrete-time states, &#xd835;&#xdc31; &#x25cf;&#xd835;&#xdc51;(&#xd835;&#xdc61;0) , by utilizing extra equations not present in the other modes (for example equations to define the start value for a state or for the derivative of a state)." ID="ID_1696147492" CREATED="1567450190905" MODIFIED="1567450190905"/>
</node>
<node TEXT="continuous-time" ID="ID_478539081" CREATED="1567450169725" MODIFIED="1567450176666">
<node TEXT="This mode is used to compute the values of all (real) continuous-time variables between events by numerically solving ordinary differential and algebraic equations. All discrete-time variables are fixed during this phase and the corresponding discrete-time equations are not evaluated." ID="ID_343305885" CREATED="1567450202201" MODIFIED="1567450202201"/>
</node>
<node TEXT="event mode" ID="ID_1481847711" CREATED="1567450177746" MODIFIED="1567450180882">
<node TEXT="This mode is used to compute new values for all continuous-time variables, as well as for all discrete-time variables that are activated at the current event instant &#xd835;&#xdc61;, given the values of the variables from the previous instant&#xd835;&#xdc61; &#x2022;. This is performed by solving algebraic equations consisting of all continuous-time and all active discrete-time equations. In FMI 2.0 there is no mechanism that the FMU can provide the information whether a discrete-time variable is active or is not active (is not computed) at an event instant. Therefore, the environment has to assume that at an event instant always all discrete-time variables are computed, although internally in the FMU only a subset might be newly computed." ID="ID_625890264" CREATED="1567450215981" MODIFIED="1567450215981"/>
</node>
</node>
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
<node TEXT="to add / modify" POSITION="right" ID="ID_519374594" CREATED="1567508200042" MODIFIED="1567510563263">
<edge COLOR="#00007c"/>
<node TEXT="initialization" ID="ID_1696874430" CREATED="1567510377438" MODIFIED="1567510380486">
<node TEXT="pre" ID="ID_100054869" CREATED="1567510380739" MODIFIED="1567510381579"/>
<node TEXT="post" ID="ID_472373736" CREATED="1567510381876" MODIFIED="1567510383022"/>
</node>
<node TEXT="add __iadd__ and __isub__ to arraywrapper" ID="ID_1398498497" CREATED="1567433801617" MODIFIED="1567433815749"/>
<node TEXT="make it resilient to complex canonical names" ID="ID_388702497" CREATED="1567424574752" MODIFIED="1567424595635">
<node TEXT="this.variables.coucou.unit" ID="ID_1454067418" CREATED="1567424595926" MODIFIED="1567424618823"/>
</node>
<node TEXT="properties level" ID="ID_443070065" CREATED="1567510881381" MODIFIED="1567510886742">
<node TEXT="default" ID="ID_1553714139" CREATED="1567175434612" MODIFIED="1567175436269">
<node TEXT="getter" ID="ID_1601526812" CREATED="1567421500997" MODIFIED="1567421509228"/>
<node TEXT="setter" ID="ID_318133146" CREATED="1567421509551" MODIFIED="1567421511203">
<node TEXT="set_prop_default" ID="ID_1271124127" CREATED="1567421648479" MODIFIED="1567421675042">
<node TEXT="lazy_data.setdefault(...)" ID="ID_374103265" CREATED="1567421675865" MODIFIED="1567421712109"/>
</node>
</node>
<node TEXT="lazy" ID="ID_1294400586" CREATED="1567349509362" MODIFIED="1567349517103">
<node TEXT="default" ID="ID_1234555235" CREATED="1567351242067" MODIFIED="1567351244265"/>
</node>
</node>
<node TEXT="exec" ID="ID_928948922" CREATED="1567421542530" MODIFIED="1567510593318">
<node TEXT="getter/setter" ID="ID_1194389498" CREATED="1567421552778" MODIFIED="1567510697271">
<node TEXT="get_xxxx" ID="ID_356389095" CREATED="1567421567203" MODIFIED="1567421573031"/>
<node TEXT="set_xxxx" ID="ID_295560963" CREATED="1567421574515" MODIFIED="1567421579286"/>
</node>
<node TEXT="formatting" ID="ID_1303152769" CREATED="1567175436697" MODIFIED="1567175438523">
<node TEXT="templating" ID="ID_1788849842" CREATED="1567349453714" MODIFIED="1567349487582"/>
<node TEXT="dependencies" ID="ID_1322641175" CREATED="1567349488150" MODIFIED="1567349491472"/>
</node>
</node>
<node TEXT="cache" ID="ID_370378295" CREATED="1567510597565" MODIFIED="1567510599705">
<node TEXT="._xxxx" ID="ID_1809004882" CREATED="1567510607967" MODIFIED="1567510613836"/>
</node>
<node TEXT="storage" ID="ID_1514432236" CREATED="1567510658101" MODIFIED="1567510659890">
<node TEXT="properties" ID="ID_1913508183" CREATED="1567349517932" MODIFIED="1567351220668">
<node TEXT="extended properties" ID="ID_1261849294" CREATED="1567351254947" MODIFIED="1567351263790"/>
</node>
</node>
<node TEXT="cache" ID="ID_736559273" CREATED="1567175626071" MODIFIED="1567175627632">
<node TEXT="getter" ID="ID_68565867" CREATED="1567421500997" MODIFIED="1567421509228">
<node TEXT="[]" ID="ID_441534409" CREATED="1567422060470" MODIFIED="1567422064373"/>
<node TEXT=".get(" ID="ID_946291431" CREATED="1567422064712" MODIFIED="1567422068743"/>
<node TEXT=".xxxxx" ID="ID_689018906" CREATED="1567422069761" MODIFIED="1567422075743"/>
<node TEXT="for_json" ID="ID_190557461" CREATED="1567422538757" MODIFIED="1567422541952"/>
</node>
<node TEXT="setter" ID="ID_828251028" CREATED="1567421509551" MODIFIED="1567421511203">
<node TEXT="[]" ID="ID_694458329" CREATED="1567422060470" MODIFIED="1567422064373"/>
<node TEXT=".set(" ID="ID_547542651" CREATED="1567422064712" MODIFIED="1567422084523"/>
<node TEXT=".xxxxx" ID="ID_510748636" CREATED="1567422069761" MODIFIED="1567422075743"/>
</node>
<node TEXT="invalidation" ID="ID_1206889960" CREATED="1567422097772" MODIFIED="1567422101278">
<node TEXT="self.__dependencies__" ID="ID_1654858070" CREATED="1567422763079" MODIFIED="1567422765225"/>
<node TEXT=".touch(" ID="ID_768916114" CREATED="1567422101447" MODIFIED="1567422107078"/>
</node>
</node>
<node TEXT="when i m a user getting a property, i only set the lazy_data of the property" ID="ID_1484223647" CREATED="1567175510519" MODIFIED="1567175583965"/>
<node TEXT="levels" ID="ID_399364856" CREATED="1567349506308" MODIFIED="1567349509016">
<node TEXT="properties" ID="ID_566521720" CREATED="1567349517932" MODIFIED="1567351220668">
<node TEXT="extended properties" ID="ID_1973558870" CREATED="1567351254947" MODIFIED="1567351263790"/>
</node>
<node TEXT="formatted/evaluated" ID="ID_150566233" CREATED="1567351221089" MODIFIED="1567351231722"/>
</node>
<node TEXT="get_prop_value" ID="ID_1439836493" CREATED="1567423990727" MODIFIED="1567423997060"/>
<node TEXT="set_prop_value" ID="ID_99754812" CREATED="1567423997370" MODIFIED="1567424000412"/>
<node TEXT="pseudo_literal" ID="ID_1356662825" CREATED="1567424109782" MODIFIED="1567424114374">
<node TEXT="_prop" ID="ID_235691359" CREATED="1567424192509" MODIFIED="1567424194466">
<node TEXT="" ID="ID_1658890432" CREATED="1567424196443" MODIFIED="1567424196443"/>
</node>
<node TEXT="_prop_value" ID="ID_1433125705" CREATED="1567424212823" MODIFIED="1567424216417"/>
<node TEXT="pseudo_literal.__prop_value" ID="ID_1478701417" CREATED="1567424002439" MODIFIED="1567424012794"/>
<node TEXT="_output_props" ID="ID_1676278966" CREATED="1567424122495" MODIFIED="1567424136819">
<node TEXT="does it make sense" ID="ID_1589906712" CREATED="1567424137258" MODIFIED="1567424144558"/>
<node TEXT="kind of, we don t take the value, just the prop..." ID="ID_845264565" CREATED="1567424368475" MODIFIED="1567424381696"/>
<node TEXT="bof" ID="ID_857175815" CREATED="1567424387436" MODIFIED="1567424388645"/>
</node>
<node TEXT="_input_props" ID="ID_866531359" CREATED="1567424148509" MODIFIED="1567424153521"/>
<node TEXT="_input_values" ID="ID_1544435668" CREATED="1567424391658" MODIFIED="1567424406003"/>
</node>
</node>
<node TEXT="revoir" ID="ID_90482449" CREATED="1567175428945" MODIFIED="1567175434158">
<node TEXT="prop" ID="ID_1220149057" CREATED="1567423259945" MODIFIED="1567423266941">
<node TEXT="list" ID="ID_1564632227" CREATED="1567423267269" MODIFIED="1567423269167"/>
<node TEXT="defined" ID="ID_728619771" CREATED="1567423271964" MODIFIED="1567423273982"/>
</node>
<node TEXT="make a test case" ID="ID_64821858" CREATED="1567424635936" MODIFIED="1567537469466">
<node TEXT="" ID="ID_638562038" CREATED="1567424641967" MODIFIED="1567424641967"/>
</node>
<node TEXT="mixins" ID="ID_1142884977" CREATED="1567535758948" MODIFIED="1567535763572">
<node TEXT="HasDefault" ID="ID_735951935" CREATED="1567537432656" MODIFIED="1567537477560">
<icon BUILTIN="help"/>
</node>
<node TEXT="HasUid" ID="ID_642455532" CREATED="1567537585445" MODIFIED="1567537588216">
<node TEXT="HasCanonicalName" ID="ID_1064054498" CREATED="1567541796130" MODIFIED="1567541819298"/>
<node TEXT="HasFlatName" ID="ID_1949897796" CREATED="1567544436944" MODIFIED="1567544475425"/>
<node TEXT="HasPrimaryKey" ID="ID_1655698445" CREATED="1567544476152" MODIFIED="1567545385800"/>
</node>
<node TEXT="HasTemplating" ID="ID_1940448892" CREATED="1567535802306" MODIFIED="1567535888077">
<node TEXT="context" ID="ID_1081698952" CREATED="1567537504147" MODIFIED="1567537506471"/>
</node>
<node TEXT="HasCache" ID="ID_720304730" CREATED="1567535764280" MODIFIED="1567535766863">
<node TEXT="for" ID="ID_825367352" CREATED="1567535767137" MODIFIED="1567535772459">
<node TEXT="ArrayWrapper" ID="ID_1952596199" CREATED="1567535772626" MODIFIED="1567535779209"/>
<node TEXT="LiteralValue" ID="ID_81178759" CREATED="1567535779858" MODIFIED="1567535782967"/>
<node TEXT="ProtocolBase" ID="ID_1018044049" CREATED="1567537401925" MODIFIED="1567537406559"/>
</node>
<node TEXT="touch" ID="ID_771513393" CREATED="1567536914383" MODIFIED="1567536916671">
<node TEXT="update the property" ID="ID_784448467" CREATED="1567537407544" MODIFIED="1567537421992"/>
<node TEXT="update all properties" ID="ID_1911250477" CREATED="1567537422292" MODIFIED="1567537427894"/>
</node>
<node TEXT="context" ID="ID_1945598100" CREATED="1567537512221" MODIFIED="1567537514307"/>
<node TEXT="inputs" ID="ID_1955557162" CREATED="1567537515311" MODIFIED="1567537518091"/>
</node>
<node TEXT="HasParent" FOLDED="true" ID="ID_598821059" CREATED="1567536009631" MODIFIED="1567536016392">
<node TEXT="touch_children" ID="ID_1830340070" CREATED="1567536927593" MODIFIED="1567536932905"/>
</node>
<node TEXT="HasDependencies" ID="ID_1816858432" CREATED="1567536022426" MODIFIED="1567536149262">
<node TEXT="Dependency" ID="ID_430967422" CREATED="1567536992223" MODIFIED="1567536997092">
<node TEXT="dependenciesKind" ID="ID_1762304112" CREATED="1567435881796" MODIFIED="1567435891153">
<node TEXT="dependent" ID="ID_243517470" CREATED="1567435893442" MODIFIED="1567435912575">
<node TEXT="no particular structure, &#x210e;(..,&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56;,..)" ID="ID_1416580842" CREATED="1567507444391" MODIFIED="1567507444391"/>
</node>
<node TEXT="constant" ID="ID_1447942032" CREATED="1567435912951" MODIFIED="1567435914623">
<node TEXT="Only for Real unknowns" ID="ID_287151668" CREATED="1567507500681" MODIFIED="1567507500681"/>
<node TEXT="constant factor" ID="ID_305923319" CREATED="1567507543902" MODIFIED="1567507543902"/>
</node>
<node TEXT="fixed" ID="ID_1877260848" CREATED="1567435914819" MODIFIED="1567435916491">
<node TEXT="fixed factor, &#xd835;&#xdc5d;&#x2219;&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56; where &#xd835;&#xdc5d; is an expression that is evaluated before fmifmi2ExitInitializationMode is called." ID="ID_380218894" CREATED="1567507576116" MODIFIED="1567507576116"/>
</node>
<node TEXT="tunable" ID="ID_717806178" CREATED="1567435916853" MODIFIED="1567435918532">
<node TEXT="tunable factor, &#xd835;&#xdc5d;&#x2219;&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56; where &#xd835;&#xdc5d; is an expression that is evaluated before fmifmi2ExitInitializationMode is called and in Event Mode due to an external event (ModelExchange) or at a Communication Point (CoSimulation)" ID="ID_1762576173" CREATED="1567507589592" MODIFIED="1567507589592"/>
</node>
<node TEXT="discrete" ID="ID_1082214309" CREATED="1567435918880" MODIFIED="1567435921440">
<node TEXT="discrete factor, &#xd835;&#xdc51;&#x2219;&#xd835;&#xdc63;&#xd835;&#xdc58;&#xd835;&#xdc5b;&#xd835;&#xdc5c;&#xd835;&#xdc64;&#xd835;&#xdc5b;,&#xd835;&#xdc56; where &#xd835;&#xdc51; is an expression that is evaluated before fmifmi2ExitInitializationMode is called and in Event Mode due to an external or internal event or at a Communication Point (CoSimulation)." ID="ID_1459666758" CREATED="1567507684362" MODIFIED="1567507686118"/>
</node>
</node>
</node>
</node>
<node TEXT="HasInit??" ID="ID_586546529" CREATED="1567536207694" MODIFIED="1567585028557">
<icon BUILTIN="button_ok"/>
<node TEXT="PreInit" ID="ID_1724483632" CREATED="1567536315020" MODIFIED="1567536317970">
<node TEXT="pre_init_hook" ID="ID_12247677" CREATED="1567585032000" MODIFIED="1567585039484"/>
</node>
<node TEXT="PostInit" ID="ID_1674386870" CREATED="1567536318738" MODIFIED="1567536321971">
<node TEXT="post_init_hook" ID="ID_1798530382" CREATED="1567585032000" MODIFIED="1567585046758"/>
</node>
<node TEXT="https://stackoverflow.com/questions/795190/how-to-perform-common-post-initialization-tasks-in-inherited-python-classes" ID="ID_584144107" CREATED="1567536460566" MODIFIED="1567536460566" LINK="https://stackoverflow.com/questions/795190/how-to-perform-common-post-initialization-tasks-in-inherited-python-classes"/>
</node>
<node TEXT="HasEvent" ID="ID_1874510657" CREATED="1567536461644" MODIFIED="1567606940105">
<icon BUILTIN="help"/>
<node TEXT="EventInfo" ID="ID_826598276" CREATED="1567536795516" MODIFIED="1567536799749">
<node TEXT="fmifmi2Boolean newDiscreteStatesNeeded;&#xd;fmifmi2Boolean terminateSimulation;&#xd;fmifmi2Boolean nominalsOfContinuousStatesChanged;&#xd;fmifmi2Boolean valuesOfContinuousStatesChanged;&#xd;fmifmi2Boolean nextEventTimeDefined;&#xd;fmifmi2Real nextEventTime;" ID="ID_1206953631" CREATED="1567537115243" MODIFIED="1567537115243"/>
</node>
<node TEXT="event handling" ID="ID_588838315" CREATED="1567510383534" MODIFIED="1567510392113">
<node TEXT="discontinuity" ID="ID_178258121" CREATED="1567510392542" MODIFIED="1567510457470"/>
<node TEXT="event indicator" ID="ID_72404677" CREATED="1567510465898" MODIFIED="1567510469789"/>
<node TEXT="USE A MIXIN" ID="ID_1222778028" CREATED="1567510478983" MODIFIED="1567510484197"/>
<node TEXT="pydispatcher" ID="ID_1902820242" CREATED="1567434118021" MODIFIED="1567434138023">
<node TEXT="http://pydispatcher.sourceforge.net/" ID="ID_1727772657" CREATED="1567434107089" MODIFIED="1567434107089" LINK="http://pydispatcher.sourceforge.net/"/>
<node TEXT="http://pydispatcher.sourceforge.net/pydoc/pydispatch.dispatcher.html" ID="ID_46218784" CREATED="1567434115782" MODIFIED="1567434115782" LINK="http://pydispatcher.sourceforge.net/pydoc/pydispatch.dispatcher.html"/>
<node TEXT="http://code.activestate.com/recipes/87056/" ID="ID_705207133" CREATED="1567434135192" MODIFIED="1567434135192" LINK="http://code.activestate.com/recipes/87056/"/>
</node>
<node TEXT="dispatcher" ID="ID_1847520408" CREATED="1567602472879" MODIFIED="1567602478291">
<node TEXT="connect" ID="ID_963828509" CREATED="1567602478557" MODIFIED="1567602480487">
<node TEXT="handler_function" ID="ID_1320433032" CREATED="1567602480754" MODIFIED="1567602562113"/>
<node TEXT="signal_name" ID="ID_58718988" CREATED="1567602487102" MODIFIED="1567602494645"/>
<node TEXT="sender" ID="ID_980349779" CREATED="1567602494934" MODIFIED="1567602498674"/>
</node>
<node TEXT="send" ID="ID_1309057307" CREATED="1567602499804" MODIFIED="1567602501192"/>
<node TEXT="handler_function" ID="ID_930762454" CREATED="1567602502856" MODIFIED="1567602599474">
<node TEXT="sender=None" ID="ID_1070791013" CREATED="1567602599648" MODIFIED="1567602627667"/>
<node TEXT="signal=None" ID="ID_702720073" CREATED="1567602601084" MODIFIED="1567602631209"/>
<node TEXT="args" ID="ID_1590961336" CREATED="1567602636827" MODIFIED="1567602638928"/>
<node TEXT="kwargs" ID="ID_1777481216" CREATED="1567602632145" MODIFIED="1567602635138"/>
</node>
</node>
</node>
<node TEXT="signals" ID="ID_1843721823" CREATED="1567603039637" MODIFIED="1567603042368">
<node TEXT="new-discrete-states-needed" ID="ID_190548163" CREATED="1567602914944" MODIFIED="1567602980366"/>
<node TEXT="terminate-simulation" ID="ID_159934584" CREATED="1567602962717" MODIFIED="1567602969079"/>
<node TEXT="nominals-of-continuous-states-changed" ID="ID_316821648" CREATED="1567602982492" MODIFIED="1567603002066">
<node TEXT="fmi2GetNominalsOfContinuousStates" ID="ID_1178083177" CREATED="1567606354566" MODIFIED="1567606354566">
<node TEXT="c" ID="ID_1684254421" CREATED="1567606322851" MODIFIED="1567606324269"/>
<node TEXT="x[]" ID="ID_1205048072" CREATED="1567606324646" MODIFIED="1567606327585"/>
<node TEXT="nx" ID="ID_1102227135" CREATED="1567606328289" MODIFIED="1567606329786"/>
<node TEXT="This function should always be called after calling function fmi2NewDiscreteStates if it returns with eventInfo-&gt; nominalsOfContinuousStatesChanged" ID="ID_1059471110" CREATED="1567606565445" MODIFIED="1567606573691"/>
</node>
</node>
<node TEXT="values-of-continuous-states-changed" ID="ID_718520471" CREATED="1567603002479" MODIFIED="1567603017669">
<node TEXT="fmi2GetContinuousStates" ID="ID_1790107407" CREATED="1567606314696" MODIFIED="1567606314696">
<node TEXT="c" ID="ID_1592077134" CREATED="1567606322851" MODIFIED="1567606324269"/>
<node TEXT="x[]" ID="ID_1190039551" CREATED="1567606324646" MODIFIED="1567606327585"/>
<node TEXT="nx" ID="ID_1776658371" CREATED="1567606328289" MODIFIED="1567606329786"/>
</node>
</node>
<node TEXT="next-event-time-defined" ID="ID_1657606701" CREATED="1567603018493" MODIFIED="1567603025712"/>
<node TEXT="nextEventTime" ID="ID_1366435509" CREATED="1567603026200" MODIFIED="1567606245724"/>
</node>
</node>
<node TEXT="FmiModel" FOLDED="true" ID="ID_1634804293" CREATED="1567606413106" MODIFIED="1567606931087">
<icon BUILTIN="messagebox_warning"/>
<node TEXT="fmi2EnterEventMode" ID="ID_285268215" CREATED="1567606704419" MODIFIED="1567606704937">
<node TEXT="The model enters Event Mode from the Continuous-Time Mode and discrete-time equations may become active (and relations are not &#x201c;frozen&#x201d;)." ID="ID_1040124511" CREATED="1567606724734" MODIFIED="1567606724734"/>
</node>
<node TEXT="fmi2NewDiscreteStates" ID="ID_1243059597" CREATED="1567606747207" MODIFIED="1567606747701">
<node TEXT="c" ID="ID_1379872773" CREATED="1567606751529" MODIFIED="1567606752538"/>
<node TEXT="EventInfo" ID="ID_723154247" CREATED="1567606752842" MODIFIED="1567606763479"/>
<node TEXT="The FMU is in Event Mode and the super dense time is incremented by this call.&#xd;If the super dense time before a call to fmifmi2NewDiscreteStates was (tR,tI) then the time instant after the call is (tR,tI+1)." ID="ID_929537615" CREATED="1567606794531" MODIFIED="1567606796378"/>
</node>
<node TEXT="fmi2GetDerivatives" ID="ID_633340641" CREATED="1567606429159" MODIFIED="1567606429159">
<node TEXT="c" ID="ID_801895772" CREATED="1567606441909" MODIFIED="1567606442905"/>
<node TEXT="derivatives" ID="ID_1656284495" CREATED="1567606443592" MODIFIED="1567606447783"/>
<node TEXT="nx" ID="ID_246310154" CREATED="1567606465511" MODIFIED="1567606469179"/>
</node>
<node TEXT="fmi2GetEventIndicators" ID="ID_690386599" CREATED="1567606440181" MODIFIED="1567606440181">
<node TEXT="c" ID="ID_1455392268" CREATED="1567606449152" MODIFIED="1567606450149"/>
<node TEXT="eventIndicators" ID="ID_202144324" CREATED="1567606450486" MODIFIED="1567606458622">
<node TEXT="The FMU must guarantee that at an event restart zj &#x2260; 0, for example by shifting zj with a small value. Furthermore, zj should be scaled in the FMU with its nominal value (so all elements of the returned vector &#x201c;eventIndicators&#x201d; should be in the order of &#x201c;one&#x201d;). The event indicators are returned as a vector with &#x201c;ni&#x201d; elements." ID="ID_534440318" CREATED="1567606514979" MODIFIED="1567606514979"/>
</node>
<node TEXT="ni" ID="ID_1986041906" CREATED="1567606458935" MODIFIED="1567606461489"/>
</node>
<node TEXT="fmi2EnterContinuousTimeMode" ID="ID_741760949" CREATED="1567606638715" MODIFIED="1567606641502">
<node TEXT="The model enters Continuous-Time Mode and all discrete-time equations become inactive and all relations are &#x201c;frozen&#x201d;.&#xd;This function has to be called when changing from Event Mode (after the global event iteration in Event Mode over all involved FMUs and other models has converged) into Continuous-Time Mode." ID="ID_1261084367" CREATED="1567606672798" MODIFIED="1567606672798"/>
</node>
</node>
</node>
<node TEXT="class" ID="ID_1173725939" CREATED="1567535806518" MODIFIED="1567535807710">
<node TEXT="CanonicalName" ID="ID_245795914" CREATED="1567535808453" MODIFIED="1567535821151">
<node TEXT="Token" ID="ID_1808506935" CREATED="1567535824334" MODIFIED="1567535828360"/>
</node>
<node TEXT="ProtocolBase" ID="ID_1184734788" CREATED="1567536908948" MODIFIED="1567536913426"/>
</node>
<node TEXT="Builder" ID="ID_813032632" CREATED="1567896191505" MODIFIED="1567896193412">
<node TEXT="tout ce qui concerne les references interclasses (cn, fmi_id, flatname) must be resolved in the builder" ID="ID_281371436" CREATED="1567754323712" MODIFIED="1567896039145"/>
<node TEXT="and  all classes created from a builder must know its builder" ID="ID_912953082" CREATED="1567896041078" MODIFIED="1567896105304"/>
<node TEXT="name_convention" ID="ID_262152688" CREATED="1567906423802" MODIFIED="1567906431842"/>
</node>
<node TEXT="Model vs Schema" ID="ID_1858255028" CREATED="1567944060432" MODIFIED="1567944064749">
<node TEXT="Model needs Schema" ID="ID_1315666004" CREATED="1567944065067" MODIFIED="1567944069531"/>
<node TEXT="Schema has no link to models" ID="ID_1643033742" CREATED="1567944069987" MODIFIED="1567944080853"/>
</node>
<node TEXT="ProtocolBase" ID="ID_1393966635" CREATED="1567907833602" MODIFIED="1567907839598">
<node TEXT="&apos;=DeclarativeBase" ID="ID_151162078" CREATED="1567895486051" MODIFIED="1567946734541"/>
<node TEXT="builder" ID="ID_282834951" CREATED="1567895498175" MODIFIED="1567896458101">
<icon BUILTIN="help"/>
</node>
<node TEXT="create_all" ID="ID_1719892141" CREATED="1567895513157" MODIFIED="1567895518304">
<node TEXT="engine" ID="ID_1057806651" CREATED="1567895510247" MODIFIED="1567895512255"/>
</node>
<node TEXT="RelationShip" ID="ID_823009920" CREATED="1567542117060" MODIFIED="1567542127967"/>
<node TEXT="ForeignKey" ID="ID_170773118" CREATED="1567542099749" MODIFIED="1567542104438">
<node TEXT="LiteralValue" ID="ID_941423526" CREATED="1567542107329" MODIFIED="1567542116316"/>
<node TEXT="declarativeBase" ID="ID_1772804035" CREATED="1567906464067" MODIFIED="1567906593664"/>
</node>
<node TEXT="create_all" ID="ID_989893004" CREATED="1567907902920" MODIFIED="1567907913057">
<node TEXT="engine" ID="ID_245759715" CREATED="1567907913291" MODIFIED="1567907915247"/>
<node TEXT="builder" ID="ID_1250379934" CREATED="1567907915549" MODIFIED="1567907917433"/>
</node>
</node>
<node TEXT="Session" ID="ID_285761345" CREATED="1567705642050" MODIFIED="1567705644101">
<node TEXT="serializers" ID="ID_1160772558" CREATED="1567706405742" MODIFIED="1567896224462"/>
<node TEXT="engines" ID="ID_12850396" CREATED="1567908396665" MODIFIED="1567908402101"/>
<node TEXT="actions" ID="ID_1815910823" CREATED="1567706412318" MODIFIED="1567754333642">
<node TEXT="commit" ID="ID_1314384639" CREATED="1567754333922" MODIFIED="1567754337511">
<node TEXT="serialize" ID="ID_1221698836" CREATED="1567754364272" MODIFIED="1567754369283">
<node TEXT="?" ID="ID_1304993707" CREATED="1567754377273" MODIFIED="1567754379666"/>
</node>
</node>
<node TEXT="query" ID="ID_122660217" CREATED="1567754337729" MODIFIED="1567754344768"/>
<node TEXT="db" ID="ID_1093343975" CREATED="1567754358729" MODIFIED="1567754363880"/>
<node TEXT="add" ID="ID_890375576" CREATED="1567895424228" MODIFIED="1567895424987"/>
<node TEXT="configure" ID="ID_1760561900" CREATED="1567895473770" MODIFIED="1567895476404">
<node TEXT="bind" ID="ID_1916065510" CREATED="1567895477032" MODIFIED="1567895479573"/>
</node>
</node>
<node TEXT="session keeps instances" ID="ID_1735517951" CREATED="1567896166887" MODIFIED="1567896177246"/>
<node TEXT="identityMap" ID="ID_1182921382" CREATED="1568025746160" MODIFIED="1568025751020">
<node TEXT="https://martinfowler.com/eaaCatalog/identityMap.html" ID="ID_1198691103" CREATED="1568025741423" MODIFIED="1568025741423" LINK="https://martinfowler.com/eaaCatalog/identityMap.html"/>
</node>
<node TEXT="https://docs.sqlalchemy.org/en/13/orm/session_basics.html" ID="ID_1256581821" CREATED="1568025796154" MODIFIED="1568025796154" LINK="https://docs.sqlalchemy.org/en/13/orm/session_basics.html"/>
<node TEXT="session keep tracks of active objects" ID="ID_1319148136" CREATED="1568127387481" MODIFIED="1568127400686">
<node TEXT="where they come from" ID="ID_1254193832" CREATED="1568127401131" MODIFIED="1568127409110">
<node TEXT="binder" ID="ID_1891413568" CREATED="1568127411997" MODIFIED="1568127414210"/>
</node>
<node TEXT="allow to query" ID="ID_897882410" CREATED="1568127415557" MODIFIED="1568127428271"/>
<node TEXT="" ID="ID_1624278735" CREATED="1568127431769" MODIFIED="1568127431769"/>
</node>
</node>
<node TEXT="PackageLoader" ID="ID_1015252795" CREATED="1567936366600" MODIFIED="1567936391802">
<node TEXT="SchemaLoader" ID="ID_1813392100" CREATED="1567936377795" MODIFIED="1567936407045"/>
<node TEXT="ModelLoader" ID="ID_888309409" CREATED="1567936935576" MODIFIED="1567936939336">
<node TEXT="ModelFactory" ID="ID_834565531" CREATED="1567936935576" MODIFIED="1567953649197"/>
<node TEXT="&apos;=Session?" ID="ID_413975219" CREATED="1567953738854" MODIFIED="1567953746723"/>
</node>
<node TEXT="packages" ID="ID_892856767" CREATED="1567953801935" MODIFIED="1567953804336"/>
<node TEXT="components" ID="ID_282814276" CREATED="1567953804665" MODIFIED="1567953808326"/>
</node>
<node TEXT="Loader" ID="ID_342384282" CREATED="1567958030002" MODIFIED="1567958033101">
<node TEXT="create" ID="ID_119856223" CREATED="1567958085506" MODIFIED="1567958200553"/>
<node TEXT="load_from_document" ID="ID_1430747608" CREATED="1567958033561" MODIFIED="1567958040447"/>
<node TEXT="load_from_uri" ID="ID_1857020858" CREATED="1567958041013" MODIFIED="1567958048008"/>
<node TEXT="load_from_file" ID="ID_634033870" CREATED="1567958048450" MODIFIED="1567958054746"/>
<node TEXT="load_from_db" ID="ID_119527935" CREATED="1567958204829" MODIFIED="1567958220276"/>
</node>
<node TEXT="Mapper" ID="ID_198381882" CREATED="1568018598121" MODIFIED="1568018601797">
<node TEXT="class_manager" ID="ID_65443850" CREATED="1568018601993" MODIFIED="1568018608828"/>
<node TEXT="class_" ID="ID_896262635" CREATED="1568018609163" MODIFIED="1568018610859"/>
<node TEXT="common_parent(other)" ID="ID_284025810" CREATED="1568025899906" MODIFIED="1568025909300"/>
<node TEXT="identity_key_from_instance(instance)" ID="ID_704473532" CREATED="1568025954008" MODIFIED="1568025976668"/>
<node TEXT="identity_key_from_primary_key(primary_key, identity_token)" ID="ID_950745145" CREATED="1568025977406" MODIFIED="1568026028406"/>
<node TEXT="identity_key_from_row(row, identity_token=None, adapter=None)" ID="ID_1916310127" CREATED="1568026032974" MODIFIED="1568026076471"/>
</node>
</node>
<node TEXT="naming convention" ID="ID_1120989888" CREATED="1567511160067" MODIFIED="1567511163130">
<node TEXT="flat" ID="ID_1079199828" CREATED="1567511170870" MODIFIED="1567511172627"/>
<node TEXT="structured" ID="ID_1309139784" CREATED="1567511172914" MODIFIED="1567511177313">
<node TEXT="canonicalName" ID="ID_1204197230" CREATED="1567511177562" MODIFIED="1567511182937"/>
</node>
</node>
</node>
<node TEXT="sqlalchemy" POSITION="right" ID="ID_1487846264" CREATED="1568147047307" MODIFIED="1568147053322">
<edge COLOR="#007c00"/>
<node TEXT="multithreading" ID="ID_1917116" CREATED="1568147054110" MODIFIED="1568147216496">
<node TEXT="https://copdips.com/2019/05/using-python-sqlalchemy-session-in-multithreading.html" ID="ID_1634498177" CREATED="1568147217334" MODIFIED="1568147217334" LINK="https://copdips.com/2019/05/using-python-sqlalchemy-session-in-multithreading.html"/>
<node TEXT="https://docs.sqlalchemy.org/en/13/orm/contextual.html#using-thread-local-scope-with-web-applications" ID="ID_990484520" CREATED="1568147934146" MODIFIED="1568147934146" LINK="https://docs.sqlalchemy.org/en/13/orm/contextual.html#using-thread-local-scope-with-web-applications"/>
</node>
</node>
<node TEXT="multithreading" POSITION="right" ID="ID_1977668079" CREATED="1568376605760" MODIFIED="1568376608913">
<edge COLOR="#7c007c"/>
<node TEXT="2 types of threads" FOLDED="true" ID="ID_1897860375" CREATED="1568377286226" MODIFIED="1568377302713">
<node TEXT="Kernel threads" ID="ID_556760602" CREATED="1568377315885" MODIFIED="1568377333606">
<node ID="ID_1975417830" CREATED="1568377629944" MODIFIED="1568377629944"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    part of the operating system
  </body>
</html>
</richcontent>
</node>
</node>
<node ID="ID_1054229556" CREATED="1568377325118" MODIFIED="1568377325118"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      User-space Threads or user threads
    </p>
  </body>
</html>
</richcontent>
<node ID="ID_134812945" CREATED="1568377642594" MODIFIED="1568377642594"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    a thread user-space thread is similar to a function or procedure call.
  </body>
</html>
</richcontent>
</node>
</node>
</node>
<node TEXT="advantages" ID="ID_1905520313" CREATED="1568377696867" MODIFIED="1568377698642">
<node ID="ID_1893963042" CREATED="1568377705061" MODIFIED="1568377705061"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    Multithreaded programs can run faster on computer systems with multiple CPUs, because theses threads can be executed truly concurrent.
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1030141280" CREATED="1568377711956" MODIFIED="1568377711956"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    A program can remain responsive to input. This is true both on single and on multiple CPU
  </body>
</html>
</richcontent>
</node>
<node ID="ID_1609973396" CREATED="1568377720436" MODIFIED="1568377720436"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    Threads of a process can share the memory of global variables. If a global variable is changed in one thread, this change is valid for all threads. A thread can have local variables.
  </body>
</html>
</richcontent>
</node>
</node>
<node ID="ID_1117736823" CREATED="1568377760522" MODIFIED="1568377760522"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    sometimes called light-weight process (LWP)
  </body>
</html>
</richcontent>
<node ID="ID_858904957" CREATED="1568377769831" MODIFIED="1568377769831"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    handling of threads is simpler than the handling of processes for an operating system
  </body>
</html>
</richcontent>
</node>
</node>
<node TEXT="library &quot;threading&quot;" ID="ID_1432529495" CREATED="1568377811269" MODIFIED="1568377825683">
<node ID="ID_785913650" CREATED="1568377842010" MODIFIED="1568377842010"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    every thread corresponds to an object.
  </body>
</html>
</richcontent>
</node>
</node>
</node>
<node TEXT="ObjectRegistry" POSITION="right" ID="ID_1751149373" CREATED="1568392647616" MODIFIED="1568392651795">
<edge COLOR="#ff0000"/>
<node TEXT="class_" ID="ID_351151707" CREATED="1568392615660" MODIFIED="1568392620824"/>
<node TEXT="key" ID="ID_385189003" CREATED="1568392610643" MODIFIED="1568392612244"/>
<node TEXT="registry" ID="ID_1391928106" CREATED="1568392605843" MODIFIED="1568392610349"/>
</node>
<node TEXT="ObjectFactory" POSITION="right" ID="ID_1465222929" CREATED="1568553051564" MODIFIED="1568553058180">
<edge COLOR="#00ff00"/>
<node TEXT="create" ID="ID_1726480737" CREATED="1568401037655" MODIFIED="1568401039498"/>
<node TEXT="create_from_document" ID="ID_1328384804" CREATED="1568401039847" MODIFIED="1568401047728"/>
<node TEXT="create_from_file" ID="ID_1915234016" CREATED="1568392678998" MODIFIED="1568392709775"/>
</node>
<node TEXT="ObjectLoader" POSITION="right" ID="ID_459779934" CREATED="1568392604145" MODIFIED="1568392647329">
<edge COLOR="#7c7c00"/>
<node TEXT="factory" ID="ID_1498991650" CREATED="1568553091000" MODIFIED="1568553093120"/>
</node>
<node TEXT="session" POSITION="right" ID="ID_116742744" CREATED="1568377262131" MODIFIED="1568390411906">
<edge COLOR="#007c7c"/>
<node TEXT="_registries" ID="ID_143576760" CREATED="1568390436433" MODIFIED="1568392718696"/>
<node TEXT="" ID="ID_1248623434" CREATED="1568392721229" MODIFIED="1568392721229"/>
<node TEXT="add_loader" ID="ID_1131080611" CREATED="1568390412116" MODIFIED="1568390415630"/>
</node>
<node TEXT="in ProtocolBase, make chidren a dict (name, child)" POSITION="right" ID="ID_1814760244" CREATED="1568477377874" MODIFIED="1568636884153">
<edge COLOR="#0000ff"/>
</node>
<node TEXT="convertir process_collection en transfo" POSITION="right" ID="ID_621618108" CREATED="1568756844024" MODIFIED="1568756881581">
<icon BUILTIN="help"/>
<edge COLOR="#00ffff"/>
</node>
<node TEXT="Handler" POSITION="right" ID="ID_1004471407" CREATED="1568638071816" MODIFIED="1568756574124">
<edge COLOR="#ff00ff"/>
<node TEXT="object_class" ID="ID_196007622" CREATED="1568756584115" MODIFIED="1568756602673"/>
<node TEXT="many" ID="ID_914905726" CREATED="1568638166940" MODIFIED="1568638168937"/>
<node TEXT="deserializer/serializer" ID="ID_1007462038" CREATED="1568638210593" MODIFIED="1568638224250"/>
<node TEXT="document" ID="ID_1801493853" CREATED="1568638144239" MODIFIED="1568756990217">
<node TEXT="url" ID="ID_898473446" CREATED="1568638154069" MODIFIED="1568638155359"/>
<node TEXT="path" ID="ID_1467315918" CREATED="1568638155852" MODIFIED="1568638158494"/>
</node>
<node TEXT="transfos" ID="ID_1742677753" CREATED="1568638195650" MODIFIED="1568756841663"/>
<node TEXT="load" ID="ID_1183283920" CREATED="1568757330283" MODIFIED="1568757349088"/>
<node TEXT="write" ID="ID_266016941" CREATED="1568757349524" MODIFIED="1568757352684"/>
</node>
<node TEXT="refacto" POSITION="right" ID="ID_16091341" CREATED="1569089445459" MODIFIED="1569089448471">
<edge COLOR="#7c0000"/>
<node TEXT="passer dans ngoschemapremium" ID="ID_175423453" CREATED="1569089449443" MODIFIED="1569089460863">
<node TEXT="keyed_object" ID="ID_1964002811" CREATED="1569089467732" MODIFIED="1569089475990"/>
<node TEXT="foreign" ID="ID_106674165" CREATED="1569089506100" MODIFIED="1569585689714"/>
</node>
</node>
<node TEXT="load_package" POSITION="right" ID="ID_521629577" CREATED="1569585690860" MODIFIED="1569585698035">
<edge COLOR="#00007c"/>
<node TEXT="args" ID="ID_1740654777" CREATED="1569585698288" MODIFIED="1569585707528">
<node TEXT="session" ID="ID_1732331458" CREATED="1569585707807" MODIFIED="1569585710254"/>
<node TEXT="filepath" ID="ID_284615619" CREATED="1569585710568" MODIFIED="1569585714740"/>
</node>
<node TEXT="function" ID="ID_1804021819" CREATED="1569585716231" MODIFIED="1569585718191">
<node TEXT="load json files recursively in filepath parent" ID="ID_1626743849" CREATED="1569585718414" MODIFIED="1569585743751"/>
<node TEXT="adds the registry to the session if not existing" ID="ID_447533415" CREATED="1569863979591" MODIFIED="1569863987963"/>
<node TEXT="adds the binder to session" ID="ID_194024666" CREATED="1569863905970" MODIFIED="1569863920970"/>
</node>
</node>
<node TEXT="session" POSITION="right" ID="ID_1469264799" CREATED="1569586033607" MODIFIED="1569586040244">
<edge COLOR="#007c00"/>
<node TEXT="object_handler" ID="ID_960024287" CREATED="1569586056229" MODIFIED="1569586084671">
<node TEXT="json" ID="ID_837012819" CREATED="1569586084998" MODIFIED="1569586098548"/>
</node>
<node TEXT="object_registry" ID="ID_528184224" CREATED="1569586174156" MODIFIED="1569586180379">
<node TEXT="key" ID="ID_1892873572" CREATED="1569586181646" MODIFIED="1569586188045"/>
</node>
<node TEXT="add_registry" ID="ID_1818964364" CREATED="1569588624386" MODIFIED="1569588628788"/>
<node TEXT="chainmap(registries)" ID="ID_443504570" CREATED="1569588632977" MODIFIED="1569588644293"/>
<node TEXT="binder" ID="ID_1602588388" CREATED="1569864550903" MODIFIED="1569885103369"/>
</node>
<node TEXT="object_handler" POSITION="right" ID="ID_1646890033" CREATED="1569588580621" MODIFIED="1569588589449">
<edge COLOR="#7c007c"/>
<node TEXT="add a read_only attribute??" ID="ID_831833894" CREATED="1569588590400" MODIFIED="1569588603036"/>
</node>
<node TEXT="uploads" POSITION="right" ID="ID_1159114331" CREATED="1569941183872" MODIFIED="1569941186478">
<edge COLOR="#007c7c"/>
<node TEXT="https://stackoverflow.com/questions/50105094/python-upload-large-files-s3-fast" ID="ID_533927725" CREATED="1569941187201" MODIFIED="1569941187201" LINK="https://stackoverflow.com/questions/50105094/python-upload-large-files-s3-fast"/>
<node TEXT="https://docs.aws.amazon.com/AmazonS3/latest/dev/transfer-acceleration.html" ID="ID_953163946" CREATED="1569941227712" MODIFIED="1569941227712" LINK="https://docs.aws.amazon.com/AmazonS3/latest/dev/transfer-acceleration.html"/>
<node TEXT="https://www.jtouzi.net/uploading-a-large-file-to-amazon-web-services-s3/" ID="ID_1102888150" CREATED="1569941998451" MODIFIED="1569941998451" LINK="https://www.jtouzi.net/uploading-a-large-file-to-amazon-web-services-s3/"/>
<node TEXT="https://github.com/boto/boto3/issues/256" ID="ID_1184201230" CREATED="1569942517003" MODIFIED="1569942520218" LINK="https://github.com/boto/boto3/issues/256">
<icon BUILTIN="messagebox_warning"/>
<node TEXT="https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#module-boto3.s3.transfer" ID="ID_1678579528" CREATED="1569942781725" MODIFIED="1569942781725" LINK="https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#module-boto3.s3.transfer"/>
</node>
</node>
<node TEXT="add clang-format to dependencies of ngomf" POSITION="right" ID="ID_1994417241" CREATED="1570952610998" MODIFIED="1570952622270">
<edge COLOR="#7c7c00"/>
</node>
<node TEXT="mindmap" FOLDED="true" POSITION="right" ID="ID_516433180" CREATED="1571088436997" MODIFIED="1571088442786">
<edge COLOR="#ff0000"/>
<node TEXT="map" ID="ID_608346309" CREATED="1571088443491" MODIFIED="1571088447636">
<node TEXT="version" ID="ID_1466488056" CREATED="1571088454538" MODIFIED="1571088456275"/>
</node>
<node TEXT="node" ID="ID_1470893863" CREATED="1571088448326" MODIFIED="1571088449917">
<node TEXT="id" ID="ID_28598897" CREATED="1571088450304" MODIFIED="1571088451533"/>
<node TEXT="text" ID="ID_1788831338" CREATED="1571088458094" MODIFIED="1571088459558"/>
<node TEXT="link" ID="ID_206964438" CREATED="1571088459981" MODIFIED="1571088461365"/>
<node TEXT="folded" ID="ID_733328510" CREATED="1571088462487" MODIFIED="1571088465371"/>
<node TEXT="color" ID="ID_1701452018" CREATED="1571088465821" MODIFIED="1571088467427"/>
<node TEXT="position" ID="ID_114308144" CREATED="1571088467677" MODIFIED="1571088470692"/>
</node>
<node TEXT="edge" ID="ID_1932260965" CREATED="1571088471435" MODIFIED="1571088473020">
<node TEXT="style" ID="ID_1308523735" CREATED="1571088493208" MODIFIED="1571088496318"/>
<node TEXT="color" ID="ID_1306076866" CREATED="1571088496701" MODIFIED="1571088501965"/>
<node TEXT="width" ID="ID_1851525413" CREATED="1571088502294" MODIFIED="1571088504256"/>
</node>
<node TEXT="font" ID="ID_1579052251" CREATED="1571088474119" MODIFIED="1571088477894">
<node TEXT="name" ID="ID_912183167" CREATED="1571088512779" MODIFIED="1571088515197"/>
<node TEXT="size" ID="ID_1905671012" CREATED="1571088515397" MODIFIED="1571088518807"/>
<node TEXT="bold" ID="ID_1061327993" CREATED="1571088519074" MODIFIED="1571088521359"/>
<node TEXT="italic" ID="ID_147763307" CREATED="1571088521610" MODIFIED="1571088525156"/>
</node>
<node TEXT="icon" ID="ID_840142111" CREATED="1571088478436" MODIFIED="1571088479431">
<node TEXT="builtin" ID="ID_273870062" CREATED="1571088528376" MODIFIED="1571088530245"/>
</node>
<node TEXT="cloud" ID="ID_44554859" CREATED="1571088480045" MODIFIED="1571088481088">
<node TEXT="color" ID="ID_1776519273" CREATED="1571088532466" MODIFIED="1571088534135"/>
</node>
<node TEXT="arrowlink" ID="ID_504422964" CREATED="1571088481287" MODIFIED="1571088491784">
<node TEXT="color" ID="ID_1714670657" CREATED="1571088536400" MODIFIED="1571088538102"/>
<node TEXT="destination" ID="ID_1538154505" CREATED="1571088539156" MODIFIED="1571088548871"/>
<node TEXT="startarrow" ID="ID_617863290" CREATED="1571088549174" MODIFIED="1571088552682"/>
<node TEXT="endarrow" ID="ID_453540235" CREATED="1571088553286" MODIFIED="1571088555657"/>
</node>
</node>
<node TEXT="https://bitbucket.org/dkuhlman/generateds/src/default/" POSITION="right" ID="ID_227246653" CREATED="1571091911653" MODIFIED="1571091916442" LINK="https://bitbucket.org/dkuhlman/generateds/src/default/">
<edge COLOR="#00ff00"/>
</node>
<node TEXT="serialize(**kwargs)" POSITION="right" ID="ID_132894143" CREATED="1571213398553" MODIFIED="1571213423362">
<edge COLOR="#ff00ff"/>
<node TEXT="remove defaults" ID="ID_1465922234" CREATED="1571213983042" MODIFIED="1571213989963"/>
</node>
<node TEXT="for_json()" POSITION="right" ID="ID_423473136" CREATED="1571213423701" MODIFIED="1571213428598">
<edge COLOR="#00ffff"/>
<node TEXT="get all members jsonified" ID="ID_189316423" CREATED="1571213957024" MODIFIED="1571213980710"/>
</node>
<node TEXT="as_dict()" POSITION="right" ID="ID_1263672833" CREATED="1571213429041" MODIFIED="1571213433099">
<edge COLOR="#7c0000"/>
</node>
<node TEXT="register" POSITION="right" ID="ID_1792282620" CREATED="1571317644636" MODIFIED="1571317727404">
<edge COLOR="#00007c"/>
</node>
<node TEXT="unregister" POSITION="right" ID="ID_1443947402" CREATED="1571317728646" MODIFIED="1571317732202">
<edge COLOR="#007c7c"/>
</node>
<node TEXT="load" POSITION="right" ID="ID_1316611676" CREATED="1571317653945" MODIFIED="1571317655973">
<edge COLOR="#007c00"/>
<node TEXT="pre_load" ID="ID_747729232" CREATED="1571317666437" MODIFIED="1571317674086">
<node TEXT="deserialize_data" ID="ID_1946159783" CREATED="1571317780971" MODIFIED="1571317789325"/>
<node TEXT="filter_data" ID="ID_393498218" CREATED="1571317789998" MODIFIED="1571317793703"/>
</node>
<node TEXT="register" ID="ID_247348889" CREATED="1571317694487" MODIFIED="1571317696990"/>
</node>
<node TEXT="commit" POSITION="right" ID="ID_1747632866" CREATED="1571317698605" MODIFIED="1571317701468">
<edge COLOR="#7c007c"/>
<node TEXT="dumps" ID="ID_166012242" CREATED="1571317820839" MODIFIED="1571317822762">
<node TEXT="pre_commit" ID="ID_93305315" CREATED="1571317701882" MODIFIED="1571317704748"/>
<node TEXT="serialize_data" ID="ID_468283910" CREATED="1571317828638" MODIFIED="1571317835236"/>
</node>
</node>
<node TEXT="merger FilterObjectHandlerMixin avec JsonEnconder?" POSITION="right" ID="ID_209027291" CREATED="1571321501992" MODIFIED="1571321523052">
<edge COLOR="#ff0000"/>
<node TEXT="only" ID="ID_1922179484" CREATED="1571321585986" MODIFIED="1571321587927"/>
<node TEXT="but" ID="ID_250826681" CREATED="1571321589061" MODIFIED="1571321590221"/>
<node TEXT="recursive" ID="ID_102651078" CREATED="1571321595653" MODIFIED="1571321598097"/>
</node>
<node TEXT="xsd" POSITION="right" ID="ID_1993610341" CREATED="1571332817785" MODIFIED="1571332820125">
<edge COLOR="#0000ff"/>
<node TEXT="xsd generator" ID="ID_698832396" CREATED="1571332821057" MODIFIED="1571332825690">
<node TEXT="https://www.freeformatter.com/xsd-generator.html" ID="ID_548691685" CREATED="1571332828067" MODIFIED="1571332828067" LINK="https://www.freeformatter.com/xsd-generator.html">
<node TEXT="using Salami Slice" ID="ID_1328053667" CREATED="1571332835177" MODIFIED="1571332841148"/>
</node>
<node TEXT="used to create" ID="ID_1563992091" CREATED="1571336916259" MODIFIED="1571336920229">
<node TEXT="amesim_spe.xsd" ID="ID_1091452719" CREATED="1571336931526" MODIFIED="1571336931528" LINK="../python-ngomf/src/ngomf/schemas/amesim_spe.xsd"/>
<node TEXT="ecore.xsd" ID="ID_1140088462" CREATED="1571336959598" MODIFIED="1571336959598" LINK="../python-ngoschemapremium/src/ngoschemapremium/schemas/ecore.xsd"/>
</node>
</node>
<node TEXT="urldefrag" ID="ID_1581982248" CREATED="1571404772041" MODIFIED="1571404773262"/>
<node TEXT="urljoin" ID="ID_1459816787" CREATED="1571404780735" MODIFIED="1571404781269"/>
</node>
<node TEXT="django-plugin" POSITION="right" ID="ID_1096814860" CREATED="1571563573833" MODIFIED="1571563577769">
<edge COLOR="#00ff00"/>
<node TEXT="static/templates/{name}" ID="ID_475029839" CREATED="1571563578427" MODIFIED="1571563702351"/>
<node TEXT="templates/{name}" ID="ID_269098549" CREATED="1571563578427" MODIFIED="1571563588917"/>
<node TEXT="templatetags" ID="ID_197527884" CREATED="1571563589913" MODIFIED="1571563594786"/>
<node TEXT="context.py" ID="ID_1792966240" CREATED="1571563596240" MODIFIED="1571563602469"/>
<node TEXT="settings.py" ID="ID_1555035821" CREATED="1571563607461" MODIFIED="1571563610965"/>
<node TEXT="models.py" ID="ID_875430082" CREATED="1571563712611" MODIFIED="1571563715723"/>
<node TEXT="settings.py" ID="ID_1267996799" CREATED="1571563717185" MODIFIED="1571563719721"/>
<node TEXT="validators.py" ID="ID_1384992149" CREATED="1571563720960" MODIFIED="1571563724484"/>
<node TEXT="admin" ID="ID_1455605432" CREATED="1571564361242" MODIFIED="1571564363245">
<node TEXT="filter.py" ID="ID_1287574306" CREATED="1571564363561" MODIFIED="1571564378450"/>
<node TEXT="widgets.py" ID="ID_825234447" CREATED="1571564365910" MODIFIED="1571564368957"/>
</node>
<node TEXT="utils" ID="ID_1256454200" CREATED="1571564418509" MODIFIED="1571564419732"/>
<node TEXT="management" ID="ID_1304267655" CREATED="1571564452977" MODIFIED="1571564456796">
<node TEXT="commands" ID="ID_450864926" CREATED="1571564457129" MODIFIED="1571564459379"/>
</node>
</node>
<node TEXT="model viz" POSITION="right" ID="ID_79015774" CREATED="1571566357142" MODIFIED="1571566369388">
<edge COLOR="#ff00ff"/>
<node TEXT="https://github.com/django-extensions/django-extensions/blob/master/django_extensions/management/modelviz.py" ID="ID_318176651" CREATED="1571566371351" MODIFIED="1571566371351" LINK="https://github.com/django-extensions/django-extensions/blob/master/django_extensions/management/modelviz.py"/>
</node>
<node TEXT="plugins important" POSITION="right" ID="ID_666376104" CREATED="1571566932933" MODIFIED="1571566943885">
<edge COLOR="#00ffff"/>
<node TEXT="django-extensions" ID="ID_1306926254" CREATED="1571566944122" MODIFIED="1571566952155">
<node TEXT="extra useful commands" ID="ID_1225166865" CREATED="1571566952474" MODIFIED="1571566958083"/>
<node TEXT="https://vimeo.com/1720508" ID="ID_1317832028" CREATED="1571568607616" MODIFIED="1571568607616" LINK="https://vimeo.com/1720508"/>
</node>
<node TEXT="sentry" ID="ID_1073733460" CREATED="1571566960458" MODIFIED="1571566961767">
<node TEXT="error/exception watcher" ID="ID_971039100" CREATED="1571566962483" MODIFIED="1571566980316"/>
</node>
<node TEXT="ChatterBot" ID="ID_923079801" CREATED="1571567147398" MODIFIED="1571567164385" LINK="https://github.com/gunthercox/ChatterBot">
<node TEXT="machine learning chat engine" ID="ID_237537646" CREATED="1571567167161" MODIFIED="1571567174760"/>
</node>
<node TEXT="django-debug-toolbar" ID="ID_1148931745" CREATED="1571567205079" MODIFIED="1571567210750">
<node TEXT="https://github.com/jazzband/django-debug-toolbar" ID="ID_1644110074" CREATED="1571567211429" MODIFIED="1571567211429" LINK="https://github.com/jazzband/django-debug-toolbar"/>
</node>
</node>
<node TEXT="django" POSITION="right" ID="ID_781679011" CREATED="1571568222899" MODIFIED="1571568225293">
<edge COLOR="#7c0000"/>
<node TEXT="views" ID="ID_1975643659" CREATED="1571568227016" MODIFIED="1571568258403">
<node TEXT="get object or object list" ID="ID_808772026" CREATED="1571568753729" MODIFIED="1571568768965"/>
<node TEXT="transform" ID="ID_1596131895" CREATED="1571568769920" MODIFIED="1571568778727"/>
<node TEXT="render template" ID="ID_1766912947" CREATED="1571568779194" MODIFIED="1571568792939"/>
</node>
<node TEXT="page" ID="ID_594869015" CREATED="1571568264967" MODIFIED="1571568269778">
<node TEXT="" ID="ID_1964197882" CREATED="1571568284297" MODIFIED="1571568284297"/>
</node>
</node>
<node TEXT="config" POSITION="right" ID="ID_1289322279" CREATED="1571624411082" MODIFIED="1571624422466">
<edge COLOR="#00007c"/>
<node TEXT="maintenancemode" ID="ID_162954843" CREATED="1571624422666" MODIFIED="1571624441229"/>
<node TEXT="comingsoon" ID="ID_1700817938" CREATED="1571624442331" MODIFIED="1571624449191"/>
<node TEXT="campain" ID="ID_1159111542" CREATED="1571624425226" MODIFIED="1571624430363"/>
<node TEXT="cms_redirects" ID="ID_776429108" CREATED="1571624472186" MODIFIED="1571624473857"/>
<node TEXT="sslify?" ID="ID_1294035359" CREATED="1571624480078" MODIFIED="1571624483519"/>
<node TEXT="stripe" ID="ID_1028201919" CREATED="1571624501931" MODIFIED="1571624504034"/>
<node TEXT="grapelli???" ID="ID_1923790682" CREATED="1571624539136" MODIFIED="1571624543438"/>
<node TEXT="satchmo" ID="ID_1777765023" CREATED="1571624561742" MODIFIED="1571624664821"/>
<node TEXT="payment" ID="ID_36277671" CREATED="1571624679628" MODIFIED="1571624683508"/>
<node TEXT="stachmo" ID="ID_1552382410" CREATED="1571624683926" MODIFIED="1571624691756"/>
<node TEXT="paypal" ID="ID_131595676" CREATED="1571624693809" MODIFIED="1571624695707"/>
<node TEXT="djstripe" ID="ID_1019223919" CREATED="1571624705480" MODIFIED="1571624707365"/>
<node ID="ID_339065697" CREATED="1571625366057" MODIFIED="1571625366057"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <pre style="background-color: #2b2b2b; color: #a9b7c6; font-family: Menlo; font-size: 9.0pt">django-templated-email</pre>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_1104591734" CREATED="1571625372765" MODIFIED="1571627842760"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <pre style="background-color: #2b2b2b; color: #a9b7c6; font-family: Menlo; font-size: 9.0pt">django-email-as_username</pre>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_1905720434" CREATED="1571625558943" MODIFIED="1571625558943"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <pre>django-filer</pre>
  </body>
</html>

</richcontent>
<node TEXT="https://django-filer.readthedocs.io/en/latest/index.html" ID="ID_1041107563" CREATED="1571625511251" MODIFIED="1571625511251" LINK="https://django-filer.readthedocs.io/en/latest/index.html"/>
<node TEXT="installed_apps" ID="ID_270733046" CREATED="1571625665685" MODIFIED="1571625671646"/>
<node TEXT="settings" ID="ID_949814909" CREATED="1571625675000" MODIFIED="1571625676554"/>
<node TEXT="urlpatterns" ID="ID_675286431" CREATED="1571625692150" MODIFIED="1571625702188">
<node TEXT="url(r&apos;^filer/&apos;, include(&apos;filer.urls&apos;))" ID="ID_1754908414" CREATED="1571625713132" MODIFIED="1571625715049"/>
</node>
<node TEXT="thumbnail processors" ID="ID_1730766187" CREATED="1571625760512" MODIFIED="1571625766204"/>
</node>
</node>
<node TEXT="DJANGO" POSITION="right" ID="ID_1258128959" CREATED="1571627664959" MODIFIED="1571627667943">
<edge COLOR="#007c00"/>
<node TEXT="plugins" ID="ID_1940134604" CREATED="1571627668953" MODIFIED="1571627806862">
<node TEXT="env" ID="ID_1391680358" CREATED="1571628645742" MODIFIED="1571628647559">
<node TEXT="django-environ" ID="ID_1110636447" CREATED="1571628649129" MODIFIED="1571628652561"/>
</node>
<node TEXT="auth" ID="ID_293464158" CREATED="1571627829740" MODIFIED="1571627832171">
<node TEXT="django-allauth" ID="ID_1373395543" CREATED="1571627807484" MODIFIED="1571627818388">
<node TEXT="description" ID="ID_1127912452" CREATED="1571628131280" MODIFIED="1571628140582">
<node TEXT="Integrated set of Django applications addressing authentication, registration, account management as well as 3rd party (social) account authentication." ID="ID_1713211696" CREATED="1571628145161" MODIFIED="1571628147411"/>
</node>
<node TEXT="homepage" ID="ID_155591470" CREATED="1571628180836" MODIFIED="1571628184035" LINK="http://www.intenct.nl/projects/django-allauth/"/>
</node>
<node TEXT="django-email-as_username" ID="ID_599301632" CREATED="1571627849369" MODIFIED="1571627850996"/>
</node>
<node TEXT="payment" ID="ID_418797961" CREATED="1571627855194" MODIFIED="1571627859321">
<node TEXT="djstripe" ID="ID_967240654" CREATED="1571627862179" MODIFIED="1571627866561"/>
<node TEXT="ngodjstripe" ID="ID_1587371561" CREATED="1571627869705" MODIFIED="1571627875684">
<node TEXT="forker djstripe?" ID="ID_1770822743" CREATED="1571627893197" MODIFIED="1571627898443">
<node TEXT="pour integrer leurs modifs et faciliter" ID="ID_1395076206" CREATED="1571627903104" MODIFIED="1571628129010"/>
</node>
</node>
</node>
<node TEXT="email" ID="ID_1045917872" CREATED="1571628424300" MODIFIED="1571628426877">
<node ID="ID_1004143763" CREATED="1571628464615" MODIFIED="1571628464615"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <pre><span class="pl-s1">django-anymail</span></pre>
  </body>
</html>

</richcontent>
<node TEXT="description" ID="ID_698148159" CREATED="1571628485591" MODIFIED="1571628489702">
<node ID="ID_1525535967" CREATED="1571628492498" MODIFIED="1571628532848"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span class="text-gray-dark mr-2" itemprop="about">Django email backends and webhooks</span>
  </body>
</html>

</richcontent>
<node ID="ID_448263464" CREATED="1571628536062" MODIFIED="1571628536062"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span class="text-gray-dark mr-2" itemprop="about">Amazon SES, Mailgun, Mailjet, Postmark, SendGrid, SendinBlue, SparkPost and more</span>
  </body>
</html>

</richcontent>
</node>
</node>
</node>
<node TEXT="homepage" ID="ID_64572124" CREATED="1571628514574" MODIFIED="1571628519928" LINK="https://anymail.readthedocs.io/"/>
</node>
</node>
<node TEXT="django-classy-tags" ID="ID_1036184450" CREATED="1571632225966" MODIFIED="1571632249830">
<node TEXT="description" ID="ID_1883030709" CREATED="1571632338121" MODIFIED="1571632341096">
<node TEXT="The goal of this project is to create a new way of writing Django template tags which is fully compatible with the current Django templating infrastructure. This new way should be easy, clean and require as little boilerplate code as possible while still staying as powerful as possible." ID="ID_1437624843" CREATED="1571632341500" MODIFIED="1571632419016"/>
<node TEXT="features" ID="ID_642845001" CREATED="1571632358842" MODIFIED="1571632361518">
<node ID="ID_1743170290" CREATED="1571632410737" MODIFIED="1571632410737"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      Class based template tags.
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_1914296382" CREATED="1571632410737" MODIFIED="1571632410737"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      Template tag argument parser.
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_122260213" CREATED="1571632410738" MODIFIED="1571632410738"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      Declarative way to define arguments.
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_1852755753" CREATED="1571632410739" MODIFIED="1571632410739"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      Supports (theoretically infinite) parse-until blocks.
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_181947030" CREATED="1571632410740" MODIFIED="1571632410740"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      Extensible
    </p>
  </body>
</html>

</richcontent>
</node>
</node>
</node>
<node TEXT="homepage" ID="ID_471010187" CREATED="1571632431326" MODIFIED="1571632436249" LINK="https://github.com/divio/django-classy-tags"/>
<node TEXT="setup" ID="ID_1626323300" CREATED="1571632507611" MODIFIED="1571632511234">
<node TEXT="requirements" ID="ID_1066757295" CREATED="1571632515063" MODIFIED="1571632521438"/>
</node>
</node>
<node ID="ID_1481689531" CREATED="1571632252303" MODIFIED="1571632252303"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      django-extensions
    </p>
  </body>
</html>

</richcontent>
<node TEXT="description" ID="ID_372127744" CREATED="1571632273802" MODIFIED="1571632278348">
<node TEXT="additional commands" ID="ID_40824919" CREATED="1571632278593" MODIFIED="1571632284866"/>
</node>
</node>
<node ID="ID_271004652" CREATED="1571632252303" MODIFIED="1571632252303"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      django-reversion
    </p>
  </body>
</html>

</richcontent>
<node TEXT="description" ID="ID_1005558705" CREATED="1571632556719" MODIFIED="1571632561862">
<node ID="ID_1485534557" CREATED="1571632574939" MODIFIED="1571632574939"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      <strong>django-reversion</strong> is an extension to the Django web framework that provides version control for model instances.
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_915097484" CREATED="1571632604782" MODIFIED="1571632604782"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      *&#160;&#160;Roll back to any point in a model instance&#8217;s history.
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_156828296" CREATED="1571632604783" MODIFIED="1571632604783"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      *&#160;&#160;Recover deleted model instances.
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_788222594" CREATED="1571632604784" MODIFIED="1571632604784"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      *&#160;&#160;Simple admin integration.
    </p>
  </body>
</html>

</richcontent>
</node>
</node>
</node>
<node TEXT="django-categories" ID="ID_1498318610" CREATED="1571637571393" MODIFIED="1571637575114">
<node TEXT="description" ID="ID_1283888571" CREATED="1571637575384" MODIFIED="1571637577261">
<node ID="ID_54770610" CREATED="1571637578021" MODIFIED="1571637578021"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <span class="text-gray-dark mr-2" itemprop="about">This app attempts to provide a generic category system that multiple apps could use. It uses MPTT for the tree storage and provides a custom admin for better visualization (copied and modified from feinCMS). </span>
  </body>
</html>

</richcontent>
</node>
</node>
<node TEXT="homepage" ID="ID_1221877518" CREATED="1571637585547" MODIFIED="1571637590346" LINK="https://github.com/callowayproject/django-categories"/>
</node>
<node ID="ID_363141577" CREATED="1571632252304" MODIFIED="1571633638102">
<icon BUILTIN="button_cancel"/>
<richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      django-rq
    </p>
  </body>
</html>

</richcontent>
</node>
<node ID="ID_912557428" CREATED="1571632252305" MODIFIED="1571632252305"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <p>
      django-coreapi
    </p>
  </body>
</html>

</richcontent>
</node>
</node>
<node TEXT="cookiecutters" ID="ID_1740701141" CREATED="1571628285823" MODIFIED="1571628289939">
<node TEXT="https://github.com/pydanny/cookiecutter-django" ID="ID_78594804" CREATED="1571628291008" MODIFIED="1571628291008" LINK="https://github.com/pydanny/cookiecutter-django">
<node TEXT="all-auth" ID="ID_1650293160" CREATED="1571628291982" MODIFIED="1571628302769"/>
<node TEXT="environ" ID="ID_253320850" CREATED="1571628303379" MODIFIED="1571628308663"/>
</node>
<node TEXT="https://github.com/pydanny/cookiecutter-djangopackage" ID="ID_1739935447" CREATED="1571646399459" MODIFIED="1571646399459" LINK="https://github.com/pydanny/cookiecutter-djangopackage"/>
</node>
<node TEXT="docker" ID="ID_1697222963" CREATED="1571649163460" MODIFIED="1571649166048">
<node ID="ID_1102745811" CREATED="1571649176028" MODIFIED="1571649176028"><richcontent TYPE="NODE">

<html>
  <head>
    
  </head>
  <body>
    <pre>docker-compose up</pre>
  </body>
</html>

</richcontent>
</node>
</node>
<node TEXT="loading 11.908553" ID="ID_612584008" CREATED="1571830306175" MODIFIED="1571850114086">
<node TEXT="10.194555" ID="ID_883963476" CREATED="1571851723193" MODIFIED="1571851723193">
<node TEXT="7.991019" ID="ID_816412447" CREATED="1571853199602" MODIFIED="1571853199602">
<node TEXT="png_4743392750190859402.png" ID="ID_960275020" CREATED="1571858695451" MODIFIED="1571858695451">
<hook URI="NGOSCHEMA_files/png_4743392750190859402.png" SIZE="1.0" NAME="ExternalObject"/>
</node>
</node>
<node TEXT="removing call to any_pprint to the new lazy_format class" ID="ID_909136264" CREATED="1571853201563" MODIFIED="1571853239552"/>
</node>
<node TEXT="memoizing short_repr" ID="ID_912976014" CREATED="1571851746312" MODIFIED="1571851763349"/>
</node>
<node TEXT="serializing 2.789402" ID="ID_408544295" CREATED="1571830306175" MODIFIED="1571850058928">
<node TEXT="2.337396" ID="ID_1379850682" CREATED="1571851730654" MODIFIED="1571851730654"/>
</node>
<node TEXT="loading 0.266558" ID="ID_962770744" CREATED="1571849779588" MODIFIED="1571849779588"/>
<node TEXT="serializing 13.782692" ID="ID_896633679" CREATED="1571849428769" MODIFIED="1571849428769"/>
</node>
</node>
</map>

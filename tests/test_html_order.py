content = """
  <body>
    <p id="onlinecourse">
      Long remained secret and restricted to circles of initiates, the 
      techniques of this <b>tantric ritual</b>&#160;are now available to you thanks 
      to our easy-to-follow course which includes:
    </p>
    <ul>
      <li>
        More than 130 slides with pictures and videos (<b>with explicit sexual 
        content</b>).
      </li>
      <li>
        Diagrams of the feminine anatomy to easily identify and locate all the 
        parts we will get to massage, such as her clitoris, her G-spot, 
        A-spot, K-spot, her cervix, etc...<br><a class="btn btn-primary span5" href="/yoni-massage/some-anatomy-first/" type="button">Learn more on feminine anatomy</a></br>
      </li>
      <li>
        Step-by-step instructions to create an amazing massage experience from 
        start to finish: learn how to give her a sensual full-body massage, 
        and then an incredible Yoni massage
      </li>
      <li>
        Clear descriptions of the different types of orgasms and how to give 
        them.<br><a class="btn btn-primary span5" href="/yoni-massage/some-anatomy-first/orgasms/" type="button">Learn more on orgasms</a></br>
      </li>
      <li>
        A brief introduction to Tantra. Understand the basic masculine and 
        feminine principles, chakras, and the role of sexual energy in this 
        spiritual practice.<br><a class="btn btn-primary span5" href="/about-tantra/">Learn more about Tantra</a></br>
      </li>
    </ul>
  </body>
"""

from ngoschema.utils import xmltodict
from pprint import pprint

html = xmltodict.parse(content)
body = html['body']
pprint(body)
print(xmltodict.unparse(html))

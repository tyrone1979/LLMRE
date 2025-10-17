import re

texts = [(
    "Outright Distribution ( formerly Screentime Partners ) is a global TV distribution company headquartered in London and owned by Warner Bros."
    "Television Productions UK .Outright specialises in format and finished programme distribution ."
    "With an expanding library from Shed Media companies ' content and growing quality third party business , "
    "Outright Distribution has a large catalogue of programme brands , selling over 2,000 hours in over 125 different territories worldwide ."
    "In Broadcast magazine 's Top Ten Most Used UK Distributors survey in March 2008 , Outright Distribution was placed 7th ."
    "Outright Distribution became part of the Shed Media Group in September 2006 ."
    "On 5 August 2010 , Warner Bros. Television secured a 55.75 % stake in Shed Media ."
    "Warner Bros. completed its acquisition of a majority stake in Shed Media on 14 October .Under"
    "the deal , Shed Media will remain an independent company but Outright Distribution would be folded into the "
    "Warner 's UK operation ."),
    """ "Direction of Endeavor for Chinese Christianity in the Construction of New China " , commonly known as  
         "The Christian Manifesto " or " The Three - Self Manifesto " , was a political manifesto of Protestants in 
         China whereby they backed the newly - founded People 's Republic of China ( PRC ) and the leadership of the 
         Communist Party of China ( CPC ) .Published in 1950 , the manifesto paved the way for the government - 
         controlled Three - Self Patriotic Movement ( TSPM ) of Protestants .This movement proclaimed the three 
         principles of self - government , self - support , and self - propagation .The drafting and content of the 
         manifesto was , and remains , controversial to this day .The manifesto was devised after Protestant leaders 
         presented their concerns with religious freedom to Zhou Enlai , the Premier of China .Instead of receiving 
         their report , Zhou demanded them to come up with a statement in support of the new communist leadership .Y. 
         T. Wu and other leftist clergymen espoused the task and presented a draft manifesto that , after some 
         opposition and changes , became a foundational text of Christianity in the new People 's Republic .It 
         condemns missionary activities in China as a form of imperialism , pledges loyalty to the communist 
         leadership , and encourages the Church to take up an indigenous Chinese stance toward Christianity 
         .Published on the front page of the People 's Daily , the manifesto was accompanied by a campaign to gather 
         signatures .Many Christian leaders and laymen signed , while others refused to do so .After the Korean War 
         broke out , the campaign became an increasingly politicized test of loyalty that became merged with the 
         Campaign to Suppress Counterrevolutionaries .Some view the manifesto as a betrayal of the Church , 
         while others find sympathy for the position of Chinese Christians struggling to reconcile their faith with 
         the changed political realities .The manifesto ended missionary activities in China and the separation of 
         church and state .It led to the founding the TSPM and brought persecution to dissidents . """,
    """jerry steiner,Jerry Steiner ( January 7 , 1918 – February 1 , 2012 ) was an American professional basketball player .He played two seasons in the National Basketball League ( NBL ) , one of the two leagues that merged to form the National Basketball Association .Steiner , a 5'7 " point guard was a basketball player for Butler University from 1937 to 1940 .He made the 1940 All - American team as a senior for the Bulldogs .After graduating from Butler , Steiner played for one season for the Indianapolis Kautskys of the NBL for the 1945–46 season .After serving in World War II until 1946 , Steiner took a job teaching and coaching at Shortridge High School in Indianapolis while playing for the Fort Wayne Zollner Pistons .He left the game after the 1946–47 season .Steiner died on February 1 , 2012 , in Bonita Springs , Florida .
""",
    """̇zmir,Tire ( ) is a populous district , as well as the center town of the same district , in İzmir Province in western Turkey .By excluding İzmir 's metropolitan area , it is one of the prominent districts of the province in terms of population and is largely urbanized at the rate of 55.8 % .Tire 's center is situated at a distance of to the south - east from the point of departure of the traditional center of İzmir ( Konak Square in Konkak ) and lies at a distance of inland from the nearest seacoast in the Gulf of Kuşadası to its west .Tire district area neighbors the district areas of Selçuk ( west ) Torbalı ( north - west ) , Bayındır ( north ) and Ödemiş ( east ) , all part of İzmir Province , while to the south it is bordered by the districts of Aydın Province .The district area 's physical features are determined by the alluvial plain of Küçük Menderes River in its northern part and in its south by the mountains delimiting the parallel alluvial valley of Büyük Menderes River flowing between Aydın and the Aegean Sea .There is a Jewish community .Advantaged by its fertile soil and suitable climate , Tire district 's economy largely relies on production and processing of agricultural products , especially of figs , cotton , corn and other grains , cash crops like tobacco and sesame , fruits like watermelons , cherries , peaches and grenadines and dry fruits like walnuts and chestnuts .Tire center has an attractive old quarter with many impressive examples of Islamic architecture , and lively Tuesday and Friday markets , where the influence of the multicultural population of the surrounding villages can be observed .These two markets on two days of the week are famous across the larger region and among visitors on excursion and tourists for the handcrafted items found on sale and they attract a large customer base .A yearly event that also draws crowds to Tire is one of the liveliest and the most rooted ( since 1403 ) celebrations in western Turkey of Nevruz Day on the third Sunday of every March .A famous local speciality is Tire kebab .
""",
    """Kiss Each Other Clean is the fourth studio album by Iron & Wine , released January 25 , 2011 via 4AD ( worldwide ) and Warner Bros. in the US .The album 's title is taken from the lyrics of " Your Fake Name Is Good Enough for Me " .The first track from the album , " Walking Far from Home , " was released on November 26 in CD single and 12 " vinyl versions as part of a special Record Store Day Black Friday event .The digital download version was released on November 30 .The song " Tree by the River " has also been released , for free download , on Iron & Wine 's website .On January 5 , Iron & Wine performed all but one song from Kiss Each Other Clean live at the Greene Space in New York City for a live broadcast on NPR 's website .The album marks a further change in style – in an interview with Spin , Beam said “ It ’s more of a focused pop record .It sounds like the music people heard in their parent ’s car growing up … that early - to - mid-’70s AM , radio - friendly music . "In 2017 it was ranked number 65 in Paste magazine 's " The 100 Best Indie Folk Albums " list ..
""",
    """mavis grind,Mavis Grind ( or , meaning " gate of the narrow isthmus " ) is a narrow isthmus joining the 
         Northmavine peninsula to the rest of the island of Shetland Mainland in the Shetland Islands , 
         UK .It is just wide at its narrowest point .It carries the main A970 road to Hillswick in the north west of 
         Shetland and is about two miles west of the settlement of Brae .Mavis Grind is said to be the only place in 
         the UK where you can toss a stone across land from the North Sea to the Atlantic Ocean .It is a regular 
         crossing point for otters , which in Shetland are sea - dwelling .In 1999 , local volunteers successfully 
         helped to demonstrate whether Viking ships could be carried across the isthmus , instead of sailing around 
         the end of the island .Remains of a late Bronze Age settlement have been found close by . """,
    """Susan J. Pharr ( born March 16 , 1944 ) is an academic in the field of political science , a Japanologist 
         , and Edwin O. Reischauer Professor of Japanese Politics , Director of Reischauer Institute of Japanese 
         Studies and the Program on U.S .- Japan Relations at Harvard University .Her current research focuses on the 
         changing nature of relations between citizens and states in Asia , and on the forces that shape civil 
         society over time .In the spring of 2008 , the Japanese government acknowledged Pharr 's life 's work by 
         conferring the Order of the Rising Sun , Gold Rays with Neck Ribbon , which represents the third highest of 
         eight classes associated with this award .Accompanying the badge of the Order was a certificate explaining 
         the award as recognition of the extent to which Prof . Pharr has " contributed to promoting intellectual 
         exchange between Japan and the United States of America , and to guiding and nurturing young Japanologists . 
         " """,
    """roald,Roald is a village in Giske Municipality in Møre og Romsdal county , Norway .The village is located on the northern part of the island Vigra .Roald is about north of the city centre of Ålesund , connected via two undersea tunnels which opened in 1987 ( and will be going through extensive upgrades starting in 2008 ) .Ålesund Airport , Vigra is south of the village of Roald .Vigra Church is located a short distance south of Roald .The village of Roald has a population ( 2013 ) of 808 , giving the village a population density of .The village of Roald was the administrative centre of the old Roald Municipality that existed from 1890 until 1964 .The former municipality was later renamed Vigra Municipality .Since 1964 , it has been a part of Giske Municipality .
""",
    """The Philippine Commission was the name of two bodies , both appointed by the President of the United States to 
    assist with governing the Philippines .The first Philippine Commission was appointed by President William 
    McKinley on January 20 , 1899 to make recommendations .The second Philippine Commission , also known as the Taft 
    Commission , was a body appointed by the President to exercise legislative and limited executive powers in the 
    Philippines .It was first appointed by President McKinley in 1900 under his executive authority .The Philippine 
    Organic Act was passed by the United States Congress in 1902 ; this enshrined into law the Commission 's 
    legislative and executive authority .As stipulated in the Philippine Organic Act , the bicameral Philippine 
    Legislature was established in 1907 , with the Commission as the upper house and the elected Philippine Assembly 
    acting as lower house .The Jones Act of 1916 ended the Commission , replacing it with an elected Philippine 
    Senate as the Legislature 's upper house . """,
    """Chauncey Bunce Brewster ( September 5 , 1848 – April 9 , 1941 ) was the fifth Bishop of the Episcopal Diocese 
    of Connecticut .Brewster was born in Windham , Connecticut , to the Reverend Joseph Brewster and Sarah Jane Bunce 
    Brewster .His father was rector of St. Paul 's Church in Windham and later became rector of Christ Church in New 
    Haven , Connecticut .His younger brother was the future bishop Benjamin Brewster .The family were descendants of 
    Mayflower passenger William Brewster .Brewster attended Hopkins Grammar School , then went to Yale College , 
    where he graduated in 1868 .At Yale he was elected Phi Beta Kappa and was a member of Skull and Bones .He 
    attended Yale 's Berkeley Divinity School the following year .He was consecrated as a bishop on October 28 , 
    1897 .He was a coadjutor bishop before being diocesan bishop from 1899 to 1928 .""",
    """ariana Cook ( born 1955 ) is an American fine art photographer specializing in black and white photography and 
    gelatin silver prints .Her work has been exhibited in the Metropolitan Museum of Art , the Museum of Modern Art , 
    the J. Paul Getty Museum , the Boston Museum of Fine Arts , the National Portrait Gallery , the Bibliothèque 
    Nationale , and the Musee d'Art Moderne .She is perhaps best known for her black and white portrait , A Couple in 
    Chicago , which captures a young Barack and Michelle Obama in their 1996 Hyde Park apartment , 
    and the accompanying interview for The New Yorker .Cook , the last surviving protégé of Ansel Adams , 
    currently resides in New York City with her husband and daughter . """,
    """Cy Becker is a neighbourhood in northeast Edmonton , Alberta , Canada and named after one of Alberta 's first bush pilots and finest wartime flying aces , Cy Becker staked his claim in history by making the first air mail delivery to remote northern communities .Since then , in recognition of his contributions and those of many others , the City of Edmonton has identified an area in Edmonton 's northeast side as Pilot Sound .Subdivision and development of the neighbourhood will be guided by the Cy Becker Neighbourhood Structure Plan ( NSP ) once adopted by Edmonton City Council .It is located within Pilot Sound and was originally considered Neighbourhood 5 within the Pilot Sound Area Structure Plan ( ASP ) .Cy Becker is bounded on the west by the McConachie neighbourhood , north by Anthony Henday Drive , east by the future Gorman neighbourhood , and south by the Brintnell and Hollick - Kenyon neighbourhoods .The community is represented by the Horse Hill Community League , established in 1972 .
""",
    """oregon,Foots Creek is an unincorporated community and census - designated place ( CDP ) in Jackson County , 
    in the U.S. state of Oregon .It lies along Oregon Route 99 near the mouth of Foots Creek , where it empties into 
    the Rogue River .Interstate 5 and Valley of the Rogue State Park are on the side of the river opposite Foots 
    Creek .For statistical purposes , the United States Census Bureau has defined Foots Creek as a census - 
    designated place ( CDP ) .The census definition of the area may not precisely correspond to local understanding 
    of the area with the same name .As of the 2010 Census , the population was 799 .The community " has been known as 
    ' Bolt ' since pioneer days . "The stream takes its name from O. G. Foot , a miner who prospected along the 
    stream in the 19th century .A post office named Foots Creek had a brief existence in this vicinity in 1878 – 79 
    .Silas Draper was the postmaster .""",
    """The National Turkey Federation ( NTF ) is the non - profit national trade association based in Washington , 
    D.C. , United States , representing the turkey industry and its allies and affiliates .NTF advocates for all 
    segments of the turkey industry , providing services and conducting activities which increase demand for its 
    members ' products .The NTF represents its members before the U.S. Congress and the various regulatory agencies , 
    such as the U.S. Department of Agriculture 's Food Safety and Inspection Service .Among members of the general 
    public , NTF is best known for its role in the National Thanksgiving Turkey Presentation , an annual ceremony 
    where a live domestic turkey is presented to the President of the United States just before Thanksgiving Day .NTF 
    began presenting the National Thanksgiving Turkey during the presidency of Harry Truman .The custom of " 
    pardoning " the turkey started with Bush I in 1989 , Two birds are brought to the White House for final selection 
    and the President invariably grants a " pardon " to both birds .Its official website , EatTurkey.com , 
    is home to thousands of turkey recipes , cooking and preparation tips , and educational information on the turkey 
    industry . """,
    """ayne Gretzky Drive is a freeway in Edmonton , Alberta , Canada .Originally Canola Drive , it was officially 
    renamed October 1 , 1999 after NHL hockey player Wayne Gretzky , as a tribute to his years with the Edmonton 
    Oilers .The same day , Wayne Gretzky 's number 99 jersey was retired at the Skyreach Centre , which lies just 
    west of Wayne Gretzky Drive , at 118  Avenue .66/75  Street is a major arterial road in east Edmonton which 
    serves residential and industrial areas .Wayne Gretzky Drive and 75  Street , both located between Whitemud 
    Drive and Yellowhead Trail , is part of Edmonton 's eastern leg of its Inner Ring Road .Wayne Gretzky Drive and 
    75   Street are part of a continuous roadway that runs from 41  Avenue  SW to 33  Street  NE ( Edmonton 's 
    northeastern city limit ) and includes portions of 66 Street and Fort Road , as well as all of Manning Drive .""",
]

text2=[
       """Although the film was not a box office success in the US , it was notably chosen in 1950 to open the convention of Ghana 's Convention People 's Party #FIBT World Championship.""",
"""The Annals of the Propagation of the Faith mentions that in 1833 after the consecration of Clément Bonnand as the Vicar Apostolic of Pondicherry , he was authorized by the Holy See to send missionaries to the Maldive Islands where the Christian faith has not reached .But there is not and has never been any Catholic territorial jurisdiction in the Maldives , but has been covered by the Archdiocese of Colombo in Sri Lanka since 1886 ."""]

regex = {
    "TIME": [
        r'[0-9]{4}\s+-\s*[0-9]{2}',  # 2024 - 08
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul('
        r'?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\s+(?:,\s+\d{4})*|'  #January 7 , 1918
        r'\b(?:\d{1,2} \w+ \d{4})|(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul('  #September 2006
        r'?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})|\d{4}s*\b|'  #5 August 2010
        r'\b\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul('
        r'?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)+\b',  #14 October
        r'\b\d{1,3}(?:,\d{3})*\s*(?:hours|minutes|seconds|days|weeks|months|years)+\b'
    ],
    "NUM": [
        r'\b\d{1,3}(?:,\d{3})*\b(?!\s*(?:hours|minutes|seconds))|(?:\bone|two|three|four|five|six|seven|eight|nine|ten\b)',
        r'\d+(?:\.\d+)?\s*%'
    ],
    "others": [
        r'\b[A-Z]+(?:.[/A-Z]+)+(?:\s+\d+)*\b',  #U.S,CMMI/ DEV 3
        r'\b[A-Z]+[0-9]+\b',  #A970
        r'\b[A-Z]+[a-zàâäèéêëîïôœùûüÿç]*\b(?:\s+[A-Z][a-zàâäèéêëîïôœùûüÿç]*)*\s+de\s+\b[A-Z]+[a-zàâäèéêëîïôœùûüÿç]*\b(?:\s+[A-Z][a-zàâäèéêëîïôœùûüÿç]+)*',
        r'\b[A-Z]+[.a-z]*\b(?:\s+\'s+)*(?:\s+[A-Z][.a-z]*)*\s+of\s+\b[A-Z]+[.a-z]*\b(?:\s+[A-Z][a-z]+)*|'  
        r'\b[A-Z]+[.a-z]*\b(?:\s+\'s(?:\s+[A-Z][.a-z]*)+)+|'   #Ghana 's Convention People 's Party
        r'\b[A-Z]+[.a-z]*\b(?:\s+[A-Z][.a-z]*)*\s+of\s+\b[A-Z]+[.a-z]*\b(?:\s+[A-Z][.a-z]+)*|'  #Edwin O. Reischauer Professor of Japanese Politics
        r'\b[A-Z]+[.a-z]*\b(?:\s+\'s+)+(?:\s+[A-Z][.a-z]*)+|'  #St Paul 's Church
        r'(?:[A-Z]+[a-z]+)+\s+-\s+(?:[A-Z]+[A-Za-z]*)+|' #The Three - Self Manifesto
        r'(?:\d+\s+)+[A-Z]+[a-z]+(?:\s+[A-Z]+[a-z]+)+|' #33  Street  NE
        r'(?:[A-Z]+)+(?:\s+[A-Z]+[A-Za-z]*)+' #FIBT World Championship
    ],
}


def print_re(result):
    print('-------------------------------------')
    for key in result.keys():
        print(f"{key}:{result[key]}")


def re_ner(text):
    results = {}
    words = text.split()
    for key in regex.keys():
        for one in regex[key]:
            result = re.findall(one, text)
            if len(result) > 0:
                if key not in results:
                    results[key] = []
                results[key] += result

    # 将result中所有的列表合并成一个大的集合，以便于快速查找
    all_values = set(value for sublist in results.values() for value in sublist)
    candidates= re.findall(r'[A-Z]+[a-zàâäèéêëîïôœùûüÿç]{2,}', ' '.join(words[1:]))
    # 遍历candidates列表
    for candidate in candidates:
        # 检查candidate是否不在all_values集合中
        if  not any(candidate in item for item in all_values):
            # 如果不在，则添加到result的'others'列表中
            results.setdefault('others', []).append(candidate)
    return results


if __name__ == '__main__':
    for text in text2:
        print_re(re_ner(text))

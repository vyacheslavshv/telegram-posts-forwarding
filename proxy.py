# from endpoints import endpoints
endpoints = {
    '+1': ('us.smartproxy.com', 10000),
    # '+1': ('ca.smartproxy.com', 20000),
    '+44': ('gb.smartproxy.com', 30000),  # GB (Great Britain)
    '+49': ('de.smartproxy.com', 20000),  # Germany
    '+33': ('fr.smartproxy.com', 40000),  # France
    '+34': ('es.smartproxy.com', 10000),  # Spain
    '+39': ('it.smartproxy.com', 20000),  # Italy
    '+46': ('se.smartproxy.com', 20000),  # Sweden
    '+30': ('gr.smartproxy.com', 30000),  # Greece
    '+351': ('pt.smartproxy.com', 20000),  # Portugal
    '+31': ('nl.smartproxy.com', 10000),  # Netherlands
    '+32': ('be.smartproxy.com', 40000),  # Belgium
    '+7': ('ru.smartproxy.com', 40000),  # Russia
    '+380': ('ua.smartproxy.com', 40000),  # Ukraine
    '+48': ('pl.smartproxy.com', 20000),  # Poland
    '+972': ('il.smartproxy.com', 30000),  # Israel
    '+90': ('tr.smartproxy.com', 30000),  # Turkey
    '+61': ('au.smartproxy.com', 30000),  # Australia
    '+60': ('my.smartproxy.com', 30000),  # Malaysia
    '+66': ('th.smartproxy.com', 30000),  # Thailand
    '+82': ('kr.smartproxy.com', 10000),  # South Korea
    '+81': ('jp.smartproxy.com', 30000),  # Japan
    '+63': ('ph.smartproxy.com', 40000),  # Philippines
    '+65': ('sg.smartproxy.com', 10000),  # Singapore
    '+86': ('cn.smartproxy.com', 30000),  # China
    '+852': ('hk.smartproxy.com', 10000),  # Hong Kong
    '+886': ('tw.smartproxy.com', 20000),  # Taiwan
    '+91': ('in.smartproxy.com', 10000),  # India
    '+92': ('pk.smartproxy.com', 10000),  # Pakistan
    '+98': ('ir.smartproxy.com', 30000),  # Iran
    '+62': ('id.smartproxy.com', 10000),  # Indonesia
    '+994': ('az.smartproxy.com', 30000),  # Azerbaijan
    '+76': ('kz.smartproxy.com', 40000),  # Kazakhstan
    '+77': ('kz.smartproxy.com', 40000),  # Kazakhstan
    '+997': ('kz.smartproxy.com', 40000),  # Kazakhstan
    '+971': ('ae.smartproxy.com', 20000),  # UAE
    '+52': ('mx.smartproxy.com', 20000),  # Mexico
    '+55': ('br.smartproxy.com', 10000),  # Brazil
    '+54': ('ar.smartproxy.com', 10000),  # Argentina
    '+56': ('cl.smartproxy.com', 30000),  # Chile
    '+51': ('pe.smartproxy.com', 40000),  # Peru
    '+593': ('ec.smartproxy.com', 20000),  # Ecuador
    '+57': ('co.smartproxy.com', 30000),  # Colombia
    '+27': ('za.smartproxy.com', 40000),  # South Africa
    '+20': ('eg.smartproxy.com', 20000),  # Egypt
    '+244': ('ao.smartproxy.com', 18000),  # Angola
    '+237': ('cm.smartproxy.com', 19000),  # Cameroon
    '+236': ('cf.smartproxy.com', 10000),  # Central African Republic
    '+235': ('td.smartproxy.com', 11000),  # Chad
    '+229': ('bj.smartproxy.com', 12000),  # Benin
    '+251': ('et.smartproxy.com', 13000),  # Ethiopia
    '+253': ('dj.smartproxy.com', 14000),  # Djibouti
    '+220': ('gm.smartproxy.com', 15000),  # Gambia
    '+233': ('gh.smartproxy.com', 43000),  # Ghana
    '+254': ('ke.smartproxy.com', 45000),  # Kenya
    '+231': ('lr.smartproxy.com', 46000),  # Liberia
    '+261': ('mg.smartproxy.com', 47000),  # Madagascar
    '+223': ('ml.smartproxy.com', 48000),  # Mali
    '+222': ('mr.smartproxy.com', 16000),  # Mauritania
    '+230': ('mu.smartproxy.com', 17000),  # Mauritius
    '+212': ('ma.smartproxy.com', 40000),  # Morocco
    '+258': ('mz.smartproxy.com', 41000),  # Mozambique
    '+234': ('ng.smartproxy.com', 42000),  # Nigeria
    '+221': ('sn.smartproxy.com', 49000),  # Senegal
    '+248': ('sc.smartproxy.com', 10000),  # Seychelles
    '+263': ('zw.smartproxy.com', 11000),  # Zimbabwe
    '+211': ('ss.smartproxy.com', 12000),  # South Sudan
    '+249': ('sd.smartproxy.com', 31000),  # Sudan
    '+228': ('tg.smartproxy.com', 32000),  # Togo
    '+216': ('tn.smartproxy.com', 33000),  # Tunisia
    '+256': ('ug.smartproxy.com', 34000),  # Uganda
    '+260': ('zm.smartproxy.com', 35000),  # Zambia
    '+93': ('af.smartproxy.com', 36000),  # Afghanistan
    '+973': ('bh.smartproxy.com', 37000),  # Bahrain
    '+880': ('bd.smartproxy.com', 41000),  # Bangladesh
    '+975': ('bt.smartproxy.com', 45000),  # Bhutan
    '+95': ('mm.smartproxy.com', 46000),  # Myanmar
    '+855': ('kh.smartproxy.com', 47000),  # Cambodia
    '+964': ('iq.smartproxy.com', 44000),  # Iraq
    '+962': ('jo.smartproxy.com', 26000),  # Jordan
    '+961': ('lb.smartproxy.com', 27000),  # Lebanon
    '+960': ('mv.smartproxy.com', 28000),  # Maldives
    '+976': ('mn.smartproxy.com', 29000),  # Mongolia
    '+968': ('om.smartproxy.com', 30000),  # Oman
    '+974': ('qa.smartproxy.com', 44000),  # Qatar
    '+966': ('sa.smartproxy.com', 45000),  # Saudi Arabia
    '+993': ('tm.smartproxy.com', 47000),  # Turkmenistan
    '+998': ('uz.smartproxy.com', 48000),  # Uzbekistan
    '+967': ('ye.smartproxy.com', 49000),  # Yemen
    '+355': ('al.smartproxy.com', 33000),  # Albania
    '+376': ('ad.smartproxy.com', 34000),  # Andorra
    '+43': ('at.smartproxy.com', 35000),  # Austria
    '+374': ('am.smartproxy.com', 42000),  # Armenia
    '+387': ('ba.smartproxy.com', 37000),  # Bosnia and Herzegovina
    '+359': ('bg.smartproxy.com', 38000),  # Bulgaria
    '+375': ('by.smartproxy.com', 39000),  # Belarus
    '+385': ('hr.smartproxy.com', 40000),  # Croatia
    '+357': ('cy.smartproxy.com', 48000),  # Cyprus
    '+420': ('cz.smartproxy.com', 26000),  # Czech Republic
    '+45': ('dk.smartproxy.com', 27000),  # Denmark
    '+372': ('ee.smartproxy.com', 28000),  # Estonia
    '+358': ('fi.smartproxy.com', 41000),  # Finland
    '+995': ('ge.smartproxy.com', 43000),  # Georgia
    '+36': ('hu.smartproxy.com', 43000),  # Hungary
    # '+90': ('hu.smartproxy.com:43000', ),  # Hungary
    '+354': ('is.smartproxy.com', 23000),  # Iceland
    '+353': ('ie.smartproxy.com', 24000),  # Ireland
    '+371': ('lv.smartproxy.com', 22000),  # Latvia
    '+423': ('li.smartproxy.com', 23000),  # Liechtenstein
    '+370': ('lt.smartproxy.com', 24000),  # Lithuania
    '+352': ('lu.smartproxy.com', 25000),  # Luxembourg
    '+377': ('mc.smartproxy.com', 10000),  # Monaco
    '+373': ('md.smartproxy.com', 11000),  # Moldova
    '+382': ('me.smartproxy.com', 12000),  # Montenegro
    '+47': ('no.smartproxy.com', 13000),  # Norway
    '+40': ('ro.smartproxy.com', 13000),  # Romania
    '+381': ('rs.smartproxy.com', 14000),  # Serbia
    '+421': ('sk.smartproxy.com', 15000),  # Slovakia
    '+386': ('si.smartproxy.com', 16000),  # Slovenia
    '+41': ('ch.smartproxy.com', 29000),  # Switzerland
    '+389': ('mk.smartproxy.com', 30000),  # Macedonia
    '+1242': ('bs.smartproxy.com', 17000),  # Bahamas
    '+501': ('bz.smartproxy.com', 18000),  # Belize
    '+1284': ('vg.smartproxy.com', 19000),  # British Virgin Islands
    '+506': ('cr.smartproxy.com', 31000),  # Costa Rica
    '+53': ('cu.smartproxy.com', 32000),  # Cuba
    '+1767': ('dm.smartproxy.com', 17000),  # Dominica
    '+509': ('ht.smartproxy.com', 18000),  # Haiti
    '+504': ('hn.smartproxy.com', 19000),  # Honduras
    '+1658': ('jm.smartproxy.com', 20000),  # Jamaica
    '+1876': ('jm.smartproxy.com', 20000),  # Jamaica
    '+297': ('aw.smartproxy.com', 21000),  # Aruba
    '+507': ('pa.smartproxy.com', 20000),  # Panama
    '+1787': ('pr.smartproxy.com', 21000),  # Puerto Rico
    '+1939': ('pr.smartproxy.com', 21000),  # Puerto Rico
    '+1868': ('tt.smartproxy.com', 22000),  # Trinidad and Tobago
    '+679': ('fj.smartproxy.com', 38000),  # Fiji
    '+64': ('nz.smartproxy.com', 39000),  # New Zealand
    '+591': ('bo.smartproxy.com', 40000),  # Bolivia
    '+595': ('py.smartproxy.com', 14000),  # Paraguay
    '+598': ('uy.smartproxy.com', 15000),  # Uruguay
    '+225': ('ci.smartproxy.com', 44000),  # Cote d`ivoire
    '+963': ('sy.smartproxy.com', 20000),  # Syria
    # '+': ('city.smartproxy.com:21000', ),  # New York
    # '+': ('city.smartproxy.com:21050', ),  # Los Angeles
    # '+': ('city.smartproxy.com:21100', ),  # Chicago
    # '+': ('city.smartproxy.com:21150', ),  # Houston
    # '+': ('city.smartproxy.com:21200', ),  # Miami
    # '+': ('city.smartproxy.com:21250', ),  # London
    # '+': ('city.smartproxy.com:21300', ),  # Berlin
    # '+': ('city.smartproxy.com:21350', ),  # Moscow
    '+84': ('vn.smartproxy.com', 46000),  # Vietnam
    '+356': ('mt.smartproxy.com', 49000),  # Malta
    # '+': ('eu.smartproxy.com:10000', ),  # Europe
    # '+': ('state.smartproxy.com:17000', ),  # Alabama
    # '+': ('state.smartproxy.com:17100', ),  # Alaska
    # '+': ('state.smartproxy.com:17200:', ),  # Arizona
    # '+': ('state.smartproxy.com:17300', ),  # Arkansas
    # '+': ('state.smartproxy.com:10000', ),  # California
    # '+': ('state.smartproxy.com:17400', ),  # Colorado
    # '+': ('state.smartproxy.com:17500', ),  # Connecticut
    # '+': ('state.smartproxy.com:17600', ),  # Delaware
    # '+': ('state.smartproxy.com:11000', ),  # Florida
    # '+': ('state.smartproxy.com:17700', ),  # Georgia (US)
    # '+': ('state.smartproxy.com:17800', ),  # Hawaii
    # '+': ('state.smartproxy.com:17900', ),  # Idaho
    # '+': ('state.smartproxy.com:12000', ),  # Illinois
    # '+': ('state.smartproxy.com:18000', ),  # Indiana
    # '+': ('state.smartproxy.com:18100', ),  # Iowa
    # '+': ('state.smartproxy.com:18200', ),  # Kansas
    # '+': ('state.smartproxy.com:18300', ),  # Kentucky
    # '+': ('state.smartproxy.com:18400', ),  # Louisiana
    # '+': ('state.smartproxy.com:18500', ),  # Maine
    # '+': ('state.smartproxy.com:18600', ),  # MaryLand
    # '+': ('state.smartproxy.com:18700', ),  # Massachusetts
    # '+': ('state.smartproxy.com:18700', ),  # Michigan
    # '+': ('state.smartproxy.com:18900', ),  # Minnesota
    # '+': ('state.smartproxy.com:19000', ),  # Mississippi
    # '+': ('state.smartproxy.com:19100', ),  # Missouri
    # '+': ('state.smartproxy.com:19200', ),  # Montana
    # '+': ('state.smartproxy.com:19300', ),  # Nebraska
    # '+': ('state.smartproxy.com:19400', ),  # Nevada
    # '+': ('state.smartproxy.com:19500', ),  # New Hampshire
    # '+': ('state.smartproxy.com:19600', ),  # New Jersey
    # '+': ('state.smartproxy.com:19700', ),  # New Mexico
    # '+': ('state.smartproxy.com:13000:', ),  # New York
    # '+': ('state.smartproxy.com:19800:', ),  # North Carolina
    # '+': ('state.smartproxy.com:19900', ),  # North Dakota
    # '+': ('state.smartproxy.com:20000', ),  # Ohio
    # '+': ('state.smartproxy.com:20100', ),  # Oklahoma
    # '+': ('state.smartproxy.com:20200', ),  # Oregon
    # '+': ('state.smartproxy.com:20300', ),  # Pennsylvania
    # '+': ('state.smartproxy.com:20400', ),  # Rhode Island
    # '+': ('state.smartproxy.com:20500', ),  # South Carolina
    # '+': ('state.smartproxy.com:20600', ),  # South Dakota
    # '+': ('state.smartproxy.com:20700', ),  # Tennessee
    # '+': ('state.smartproxy.com:14000', ),  # Texas
    # '+': ('state.smartproxy.com:20800', ),  # Utah
    # '+': ('state.smartproxy.com:20900', ),  # Vermont
    # '+': ('state.smartproxy.com:15000', ),  # Virginia
    # '+': ('state.smartproxy.com:16000', ),  # Washington
    # '+': ('state.smartproxy.com:21000', ),  # West Virginia
    # '+': ('state.smartproxy.com:21100', ),  # Wisconsin
    # '+': ('state.smartproxy.com:21200', ),  # Wyoming
}


def get_proxy(_number: str,proxy_type="telethon"):
    if proxy_type == "telethon":
        proxy = {
            'proxy_type': 'http',
            'addr': 'il.smartproxy.com',
            'port': 30000,
            'username': 'Software2',
            'password': 'qc42WED',
        }
        number = ''.join(n for n in _number if n.isdigit() or n == '+')
        number = '+' + number if not number.startswith('+') else number
        for code in endpoints:
            if number.startswith(code):
                proxy['addr'] = endpoints[code][0]
                proxy['port'] = endpoints[code][1]

        return proxy
    else:
        proxy = {
        "scheme": "http",  # "socks4", "socks5" and "http" are supported
        "hostname": "il.smartproxy.com",
        "port": 30000,
        "username": "Software2",
        "password": "qc42WED"
    }

        number = ''.join(n for n in _number if n.isdigit() or n == '+')
        number = '+' + number if not number.startswith('+') else number
        for code in endpoints:
            if number.startswith(code):
                proxy['hostname'] = endpoints[code][0]
                proxy['port'] = endpoints[code][1]

        return proxy


if __name__ == "__main__":
    proxy = get_proxy("528713271146")
    # print("Proxy:",proxy)
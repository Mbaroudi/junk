$TTL    86400
@               IN SOA  ns.rubi.ru. administrator.rubin.ru. (
                2006021701 ; serial
                7200       ; refresh
                3600       ; retry
                604800     ; expire
                86400      ; default_ttl
                )

@               IN NS   ns.rubi.ru.
;@              IN NS   dns1.comstar.ru.
;@              IN NS   ns.rubin.ru.
                A       172.16.0.13

localhost       IN A    127.0.0.1
ns              IN A    172.16.1.1
chat		IN A	172.16.0.14
;www             IN A    172.16.0.13
*               IN A    172.16.0.13


from http.server import HTTPServer, BaseHTTPRequestHandler
from pg import DB


class requestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        page = ""
        if(self.path == "/" or self.path == "/index"):
            try:
                page = open(
                    "/home/master/Desktop/Bil_441/WEB/Program.html").read()
                # listeye dersler yerleştiririlir
                db = DB(dbname='Bil_441', host='localhost',
                        port=5432, user='postgres', passwd='123')
                branches = db.query(
                    "SELECT b.id as \"branch-id\",* FROM public.\"Branch\" as b,public.\"Lesson\" as l where b.\"lesson-id\"=l.\"id\"").dictresult()
                list_element = "<li class=\"list-group-item d-flex justify-content-between align-items-center\">@name<input type=\"checkbox\" class=\"coursecheck coursecheckleft\" value=\"@value\"></li>"
                
                counter = {}
                saver = {}
                for branch in branches:
                    if(branch['lesson-id'] not in counter):
                        counter[branch['lesson-id']] = 0
                    counter[branch['lesson-id']] = counter[branch['lesson-id']] + 1
                    saver[str(branch['branch-id'])] =  branch['name']+"."+str(counter[branch['lesson-id']])
                    element = list_element.replace("@name", branch['name']+"."+str(counter[branch['lesson-id']]))
                    element = element.replace("@value",str(branch['branch-id']))
                    page = page.replace("@class-list", element+"@class-list")

                page = page.replace("@class-list","")

                bookmark = "<a href=\"#\" class=\"get_all_overlapped_courses\" data-day=\"@day\" data-hour=\"@hour\" data-toggle=\"tooltip\" title=\"\" data-original-title=\"Çakısan Tüm Dersler\">+</a>"
                bookcontent = "<span style=\"display: none;\" class=\"@class\">@dotname<span data-toggle=\"tooltip\" data-placement=\"right\" title=\"\" data-original-title=\"@name | @teacher \"><i class=\"fas fa-info-circle\"></i></span><br><br></span>"
                
                for branch in branches:
                    for time in range(8,19):
                        interval = branch['time-interval']['Time']
                        for i in interval:
                            start = int(i['begin'].split(":")[0]) 
                            end = int(i['end'].split(":")[0])

                            if(time >= start and time < end):
                                bk = bookmark.replace("@day",str(self.daycode(i['day'])))
                                bk = bk.replace("@hour",str(time))

                                bc = bookcontent.replace("@class","c"+str(branch['branch-id']))
                                bc = bc.replace("@dotname",saver[str(branch['branch-id'])])
                                bc = bc.replace("@name",branch['name'])

                                page = page.replace(bk,bk+bc)

                self.send_response(200)
            except:
                page = "<b>"+"We all love Bil 441"+"</b>"
                self.send_response(404)

        self.send_header('content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(page, 'utf-8'))

    def daycode(self, day):
        dic = {'monday':1,'tuesday':2,'wednesday':3,'thursday':4,'friday':5,'saturday':6,'sunday':7}
        return dic[day]

def main():
    address = ('localhost', 8080)
    server = HTTPServer(address, requestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()

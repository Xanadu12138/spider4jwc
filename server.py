
import web
import spider

urls = (
    "/curriculum", "curriculum"
)
app = web.application(urls, globals())

class curriculum:
   
    def POST(self):
        data=web.input()
        with open("log.txt","a") as file:
            file.write(str(data)+"\n")
        web.header('content-type','text/html')
        return spider.carwling(data.username,data.password)
    def GET(self):
        return "Helloworld"
if __name__ == "__main__":
    app.run()

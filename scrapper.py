from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review",methods = ['POST','GET'])
def info():
    if request.method == 'POST':
        try:
            search_string = request.form['content']
            product = search_string
            if " " in search_string:
                search_string = search_string.replace(" ","%20")
            flipkart_url = flipkart_url = "https://www.flipkart.com/search?q=" + search_string
            
            uclient = uReq(flipkart_url)
            flipkart_page = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkart_page,'html.parser')
            
            bigboxes = flipkart_html.findAll('div',{"class":"_1AtVbE col-12-12"})

            del bigboxes[0:3]
            box = bigboxes[0]
            # print(box)
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            
            prod_res = requests.get(product_link)
            prod_res.encoding = 'utf-8'
            prod_html = bs(prod_res.text,'html.parser')
            comment_boxes = prod_html.find_all('div',{'class':"_16PBlm"})

            file_name = product+'.csv'
            fw = open(file_name,'w')
            headers = "Product, Customer Name,Rating,Heading,Comment \n"
            fw.write(headers)

            reviews = []
            print('goin for comments')
            print(len(comment_boxes))
            for commentbox in comment_boxes:
                try:
                    
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    
                except:
                    logging.info('name')
            
            
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'
                    logging.info('rating')

                try:
                    
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                try:
                    product_name = prod_html.findAll('span',{'class':'B_NuCI'})[0].text
                except:
                    product_name = 'No Name'
                    logging.info(product_name)
                
                product_dict = {'Product':product_name,'Name':name,'Rating':rating,'CommentHead':commentHead,'Comment':custComment}
                print('\n',product_dict)
                reviews.append(product_dict)
            # for i in review:
            #     print(i,'\n')
            try:
                client = pymongo.MongoClient("mongodb+srv://maninder:7512@cluster0.msgslql.mongodb.net/?retryWrites=true&w=majority")
                db = client['review_scrap']
                review_col = db['review_scrap_data']
                review_col.insert_many(reviews)
            except Exception as e:
                print('database error : ',e)
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        
        

        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
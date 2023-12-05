import pytesseract
from wsgiref.simple_server import make_server
import falcon
from pdf2image import convert_from_path
import requests
import json
from os import remove
import pandas as pd
import csv


class ConverterPDF:
    def on_post(self, req, resp, uuid_lectura):
        data = req.stream.read(req.content_length or 0)
        doc = json.loads(data)
        print(doc)
        response = requests.get(doc["URL"])
        use_header = doc["header"]
        use_footer = doc["footer"]
        print("use header")
        print(use_header)
        print("use footer")
        print(use_footer)
        open(f"lecturas/{uuid_lectura}.pdf", "wb").write(response.content)
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_TEXT 
        conf = r'-l spa'
        images = convert_from_path(f'lecturas/{uuid_lectura}.pdf')
        strAllText = ''
        for i in range(len(images)):
            d = pytesseract.image_to_data(images[i],output_type=pytesseract.Output.DICT,config=conf)
            d_df = pd.DataFrame.from_dict(d)
            line_3 = d_df.loc[d_df['level'] == 3].index.values
            index_to_delete = []
            result = map(lambda x: x - 2, line_3)
            for i in list(result):
                if (d_df.loc[[i]]["block_num"].values[0] == 0) or ((len(d_df.loc[[i]]["text"].values[0]) > 0) 
                                                                   and ("." not in d_df.loc[[i]]["text"].values[0])):
                    index_to_delete.append(i + 2)
            d_df.loc[d_df['level'] == 3,["text"]] = "\n"
            d_df.drop(index_to_delete,inplace=True)
            if use_footer == True:
                block_num = int(d_df.loc[d_df['level'] == 2,['block_num']].max())
                foot_index = d_df[d_df['block_num'] == block_num].index.values
                d_df.drop(foot_index,inplace=True)
            if use_header == False:
                head_index = d_df[d_df['block_num']==1].index.values
                d_df.drop(head_index,inplace=True)
            aux = " ".join(d_df.loc[(d_df['level'] == 3) | (d_df['level'] == 5),'text'].values)
            strAllText = strAllText + aux
        remove(f"lecturas/{uuid_lectura}.pdf")
        strAllText = strAllText.replace("\n ","\n")
        resp.text = strAllText
        
        
app = falcon.App()

converter = ConverterPDF()

app.add_route('/converter/{uuid_lectura}', converter)

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
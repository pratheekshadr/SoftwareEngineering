import csv
import hashlib

import base64, os

images_list =[]

for i in range(1,51):
    filename = str(i)+'.jpg'
    path = os.path.join('images/'+filename)
    with open(path, "rb") as img_file:
        print(path)
        images_list.append(base64.b64encode(img_file.read()))
        images_list[-1] = str("data:image/jpeg;base64,"+images_list[-1].decode())

with open('database/recipeDB.csv') as fp:
    csv_reader = csv.reader(fp, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:       
            with open('database/recipe.csv', 'w',  newline='') as writeFile:    
                new_row = ['hashValue', 'name', 'procedure', 'time', 'cuisine', 'vegNonVeg', 'mealType', 'author', 'likes', 'image' ]
                wr = csv.writer(writeFile, dialect='excel')
                wr.writerow(new_row)
            writeFile.close()
                
        else:
            name = row[1]
            procedure = row[2]
            time = row[3]
            cuisine = row[4]
            vegNonVeg = row[5]
            mealType = row[6]
            author = row[7]
            likes = row[8]
            image = images_list[line_count-1]
            hashValue = hash((name, procedure, author))
            new_row = [hashValue, name, procedure, time, cuisine, vegNonVeg, mealType, author, likes, image ]
            with open('database/recipe.csv', 'a',  newline='') as writeFile:
                wr = csv.writer(writeFile, dialect='excel')
                wr.writerow(new_row)

        line_count+=1
        # if(line_count>5):
        #     break

fp.close()

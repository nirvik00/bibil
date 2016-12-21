import os
import rhinoscriptsyntax as rs

print (os.getcwd())
obj_name='residential'.lower()
f=open('ruleset.dat','r')
es_parcel_length=15
es_parcel_width=50
es_parcel_length_num=6
es_parcel_width_num=3
while True:
    x=f.readline()
    if not x:
        break
    else:
        x_name=x.split('>>')[0].lower()
        if(obj_name==x_name):
            x_field=x.split('>>')[1]
            x_value=x.split('>>')[2].split('-')[0]
            print(str(x_field)+" : "+str(x_value))
            if(str(x_field).lower()=='parcel_length'):
                es_parcel_length=x_value
            if(str(x_field).lower()=='parcel_width'):
                es_parcel_width=x_value
            if(str(x_field).lower()=='parcel_length_number'):
                es_parcel_length_num=x_value
            if(str(x_field).lower()=='parcel_width_number'):
                es_parcel_width_num=x_value

arr=([es_parcel_length,es_parcel_width,es_parcel_length_num,es_parcel_width_num])
print(arr)
f.close()
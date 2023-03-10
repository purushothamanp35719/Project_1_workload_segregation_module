from operator import index
import secrets
import streamlit as st
import io
import pandas as pd
import openpyxl

import requests
from pprint import pprint

import streamlit as st
from streamlit_option_menu import option_menu



footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}   

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Created by <a style='display: block; text-align: center;'target="_blank">Purushothaman P (purushothaman.p@nielseniq.com)</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)



def Insert_row(row_number, df, row_value):
    # Starting value of upper half
    start_upper = 0
  
    # End value of upper half
    end_upper = row_number
  
    # Start value of lower half
    start_lower = row_number
  
    # End value of lower half
    end_lower = df.shape[0]
  
    # Create a list of upper_half index
    upper_half = [*range(start_upper, end_upper, 1)]
  
    # Create a list of lower_half index
    lower_half = [*range(start_lower, end_lower, 1)]
  
    # Increment the value of lower half by 1
    lower_half = [x.__add__(1) for x in lower_half]
  
    # Combine the two lists
    index_ = upper_half + lower_half
  
    # Update the index of the dataframe
    df.index = index_
  
    # Insert a row at the end
    df.loc[row_number] = row_value
   
    # Sort the index labels
    df = df.sort_index()
  
    # return the dataframe
    return df


with st.sidebar:
    
    app_mode = option_menu(None, ["Prework-Fresh","GIC Prediction"],
                        icons=['sliders','kanban'],
                        menu_icon="app-indicator", default_index=0,
                        styles={
        "container": {"padding": "5!important", "background-color": "#f0f2f6"},
        "icon": {"color": "orange", "font-size": "28px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#2C3845"},
    }
    )


#mycondition = ["UNC","UNC_N","CPN","TURKEY","SAVEMART"]


if app_mode == "Prework-Fresh":

    st.title(" Welcome To LAC PreWork Page")

    con = st.selectbox("Please Select The Combination Type",["Des&Dept Desc&Supp Desc","Lac code&Desc&Supp Desc"])
    prework_set = st.selectbox("Please Select The Prework Set",["Set1","Set2","Set3","Set4","Set5","Set6"])
    d = st.date_input("Please Select The Pre Work Date")

    if con == "Des&Dept Desc&Supp Desc":

        con1 = "Best Received External Description"
        con2 = "Department Description"
        con3 = "Supplier Description"

    if con == "Lac code&Desc&Supp Desc":

        con1 = "External Code"
        con2 = "Best Received External Description"
        con3 = "Supplier Description"


    
    page = st.selectbox("Please Select The Pre-Work Type", ["No Selection","PreWork With Consolidated File","PreWork Without Consolidated File","PreWork Fresh Allocation"]) 

    if page == "PreWork With Consolidated File":

        output = io.BytesIO()
        output_n = io.BytesIO()
        st.subheader("Welcome To PreWork With Consolidated File")

        input_file_consol = st.file_uploader("Upload a CSV OWB Consolidation File", type=['csv'])
        input_file = st.file_uploader("Upload a CSV OWB File",type=['csv'])
        input_file_2 = st.file_uploader("Upload a XLSX PreWork Condition File",type=['xlsx'])




        if (input_file is not None) and input_file.name.endswith(".csv") and (input_file_2 is not None) and input_file_2.name.endswith(".xlsx") and (input_file_consol is not None) and input_file_consol.name.endswith(".csv") and d != "":

            try:
                df1 = pd.read_csv(input_file_consol,converters={'Department Code': lambda x: str(x)},encoding="unicode_escape")
            except:
                df1 = pd.read_csv(input_file_consol,converters={'Department Code': lambda x: str(x)})
            

            consol_1 = df1.copy()
            try:
                df2 = pd.read_csv(input_file,converters={'Department Code': lambda x: str(x)},encoding="unicode_escape")
            except:
                df2 = pd.read_csv(input_file,converters={'Department Code': lambda x: str(x)})

            df1["CON"] = df1["External Code"].astype(str)+df1["Processing Group Code"]+df1["Seq"].astype(str)
            df2["CON"] = df2["External Code"].astype(str)+df2["Processing Group Code"]+df2["Seq"].astype(str)
            df1["Test"] = "Yes"
            df1_1 = df1[["CON","Test"]]
            df3 = pd.merge(df2,df1_1,on='CON', how='left')
            df3['Test'] = df3['Test'].fillna("NA")
            df4 = df3[df3["Test"] == "NA"]
            del df4['CON']
            del df4['Test']

            del df1['CON']
            del df1['Test']
        


            owb1 = df4.copy()

            owb1["PreWork Date"]=d
            owb1['Process']=""
            owb1['Consolidated Items'] = ""

            owb1['Best Received External Description'] = owb1['Best Received External Description'].fillna(0)

            row_count = len(owb1)

            #--------------------------------------------------------------------------

            outlet = pd.read_excel(input_file_2, sheet_name = "outlet")
            bir = pd.read_excel(input_file_2, sheet_name = "bir")


            #owb1['Outlet'] = ""

            owb2 = pd.merge(owb1,outlet, on='Processing Group Code', how='left')
            owb = pd.merge(owb2,bir,on='Processing Group Code', how='left')

            owb['Outlet'] = owb['Outlet'].fillna(0)               
            owb['BIR'] = owb['BIR'].fillna("NA")


            #--------------------------------------------------------------------------

            con_df = pd.read_excel(input_file_2,sheet_name="Sub_Group")

            mycondition_1 = list(con_df["Sub_Group_Name"])
            mycondition = []

            for i in range(len(mycondition_1)):
                txt_1 = mycondition_1[i]
                txt = str(txt_1).upper()
                if (txt not in mycondition):
                    mycondition.append(txt)


            #--------------------------------------------------------------------------


            pw = pd.read_excel(input_file_2, sheet_name = "equal")

            pw_row_count = len(pw)

            mycondition_count = len(mycondition)

            for i in range(mycondition_count):
                con_word_1 = mycondition[i]
                con_word = str(con_word_1).upper()
            
                
                mycondition_n = []
                for i in range(pw_row_count):
                    txt = pw.loc[i,"Process"]
                    txt2 = pw.loc[i,"Key Words"]
                    if txt.upper() == con_word:
                        mycondition_n.append(txt2)



                mycondition_n_count = len(mycondition_n)

                for j in range(mycondition_n_count):
                    mycondition_txt = mycondition_n[j]
                    for i in range(row_count):
                        if con_word == "SAVEMART":
                            txt = owb.loc[i,'Processing Group Code']
                            if str(mycondition_txt).upper() == str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                    owb.loc[i,'Process'] = con_word
                        elif con_word == "IN SCOPE ORG":
                            txt = owb.loc[i,'Processing Group Code']
                            if str(mycondition_txt).upper() in str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                    owb.loc[i,'Process'] = con_word

                        elif con_word=="UNC" or con_word=="CPN" or con_word=="TURKEY" or con_word=="SAVEMART":
                            txt = owb.loc[i,'Best Received External Description']
                            if str(mycondition_txt).upper() == str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                    owb.loc[i,'Process'] = con_word
                        else:
                            txt = owb.loc[i,'Best Received External Description']
                            if str(mycondition_txt).upper() == str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0 and owb.loc[i,'Consolidated Items']=="":
                                    owb.loc[i,'Consolidated Items'] = con_word



            #----------------------------------------------------------------

            pw = pd.read_excel(input_file_2, sheet_name = "contain")

            pw_row_count = len(pw)

            mycondition_count = len(mycondition)

            for i in range(mycondition_count):
                
                con_word_1 = mycondition[i]
                con_word = str(con_word_1).upper()
                

                mycondition_n = []
                for i in range(pw_row_count):
                    txt = pw.loc[i,"Process"]
                    txt2 = pw.loc[i,"Key Words"]
                    if txt.upper() == con_word:
                        mycondition_n.append(txt2)



                mycondition_n_count = len(mycondition_n)

                for j in range(mycondition_n_count):
                    mycondition_txt = mycondition_n[j]
                    for i in range(row_count):
                        if con_word == "SAVEMART":
                            txt = owb.loc[i,'Processing Group Code']
                            if str(mycondition_txt).upper() in str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                    owb.loc[i,'Process'] = con_word

                        elif con_word == "IN SCOPE ORG":
                            txt = owb.loc[i,'Processing Group Code']
                            if str(mycondition_txt).upper() in str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                    owb.loc[i,'Process'] = con_word
                        elif con_word=="UNC" or con_word=="CPN" or con_word=="TURKEY" or con_word=="SAVEMART":

                            txt = owb.loc[i,'Best Received External Description']
                            if str(mycondition_txt).upper() in str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                    owb.loc[i,'Process'] = con_word
                        else:
                            txt = owb.loc[i,'Best Received External Description']
                            if str(mycondition_txt).upper() in str(txt).upper():
                                if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0 and owb.loc[i,'Consolidated Items']=="":
                                    owb.loc[i,'Consolidated Items'] = con_word

            for i in range(row_count):
                txt = owb.loc[i,'External Code']
                txt2 = owb.loc[i,'Process']
                txt3 = owb.loc[i,"Outlet"]
                nsd = txt[0:2]

                if nsd == "XX" and txt2 == "":
                    owb.loc[i,'Process'] = "NSD XX"



            for i in range(row_count):
                txt = owb.loc[i,'External Code']
                txt2 = owb.loc[i,'Process']
                txt3 = owb.loc[i,"Outlet"]

                if txt[0:3] == "'02" and txt2 == "" and  txt3 == "FOOD":
                    owb.loc[i,'Process'] = "Fresh 02"

            for i in range(row_count):
                txt = owb.loc[i,'External Code']
                txt2 = owb.loc[i,'Process']
                txt3 = owb.loc[i,"Outlet"]

                if txt[0:3] == "'02" and txt2 == "" and  txt3 == "CONV":
                    owb.loc[i,'Process'] = "Fresh 02"


            for i in range(row_count):
                txt = owb.loc[i,'External Code']
                txt2 = owb.loc[i,'Process']
                txt3 = owb.loc[i,"Outlet"]
                nsd = txt[0:2]

                if txt2 == "" and txt3 != 0 and nsd != "XX":
                    owb.loc[i,'Process'] = "Non Fresh"

            for i in range(row_count):
                txt = owb.loc[i,'Processing Group Description']
                txt2 = owb.loc[i,'Process']
                txt3 = owb.loc[i,"Outlet"]
                rsi = txt[-4:]

                if txt3 != "RSI" and rsi == " RSI":
                    owb.loc[i,'Process'] = "RSI"
                    owb.loc[i,'Outlet'] = "RSI"

            owb["Set"] = prework_set

            #for i in range(row_count):
            #    txt = owb.loc[i,'External Code']
            #    txt2 = owb.loc[i,'Process']
            #    txt3 = owb.loc[i,"Outlet"]
            #    
            #    if txt[0:3] == "'04" and txt2 == "" and txt3 != "":
            #        owb.loc[i,'Process'] = "Non Fresh"


            #owb.to_csv("new_owb.csv")


            fresh = owb[owb['Process'] == "Fresh 02"]
            nonfresh = owb[owb['Process'] == "Non Fresh"]
            nsd_xx = owb[owb['Process']=="NSD XX"]
            rsi = owb[owb['Outlet']=="RSI"]
            unknow = owb[owb['Outlet'] == 0]

            fresh_row = len(fresh)
            fresh["CONCATENATE"]=""
            fresh["T/F"]=""

            fresh.reset_index(drop=True, inplace=True)

            fresh_row = len(fresh)
            for i in range(fresh_row):
                txt1 = str(fresh.loc[i,"BIR"])
                txt2 = str(fresh.loc[i,con1])
                txt3 = str(fresh.loc[i,con2])
                txt4 = str(fresh.loc[i,con3])
                t1 = txt2.replace(" ","")
                t2 = txt3.replace(" ","")
                t3 = txt4.replace(" ","")

                txt5 = t1+t2+t3


                fresh.loc[i,"CONCATENATE"] = txt5

            
            fresh_bir = fresh[fresh['BIR'] != "NA"]
            fresh_nonbir = fresh[fresh['BIR'] == "NA"]

            fresh_bir = fresh_bir.sort_values('CONCATENATE', ascending=False)
            con_table = fresh_bir.groupby(['CONCATENATE'])['External Code'].count().reset_index()
            con_table.rename({'External Code':'Count If'}, axis=1, inplace=True)
            con_table["Unique Number"] = ""

            con_table_row = len(con_table)

            for i in range(con_table_row):
                if i < con_table_row:
                    con_table.loc[i,"Unique Number"] = i+1
                
            fresh_2 = pd.merge(fresh_bir,con_table, on='CONCATENATE', how='right')

            fresh_2.reset_index(drop=True, inplace=True)
            fresh_row_bir = len(fresh_2)
            for i in range(fresh_row_bir):
                if i < fresh_row_bir-1: 
                    j = i+1

                    txt1 = fresh_2.loc[i,"CONCATENATE"]
                    txt2 = fresh_2.loc[j,"CONCATENATE"]
                    if txt1 != "":
                        if txt1 == txt2:
                            fresh_2.loc[i,"T/F"] = "TRUE"
                        else:
                            fresh_2.loc[i,"T/F"] = "FALSE"

            fresh_nonbir = fresh_nonbir.sort_values('CONCATENATE', ascending=False)
            con_table = fresh_nonbir.groupby(['CONCATENATE'])['External Code'].count().reset_index()
            con_table.rename({'External Code':'Count If'}, axis=1, inplace=True)
            con_table["Unique Number"] = ""

            con_table_row = len(con_table)

            for i in range(con_table_row):
                if i < con_table_row:
                    con_table.loc[i,"Unique Number"] = i+1

            fresh_3 = pd.merge(fresh_nonbir,con_table, on='CONCATENATE', how='right')

            fresh_3.reset_index(drop=True, inplace=True)
            fresh_row_nonbir = len(fresh_3)
            for i in range(fresh_row_nonbir):
                if i < fresh_row_nonbir-1: 
                    j = i+1

                    txt1 = fresh_3.loc[i,"CONCATENATE"]
                    txt2 = fresh_3.loc[j,"CONCATENATE"]
                    if txt1 != "":
                        if txt1 == txt2:
                            fresh_3.loc[i,"T/F"] = "TRUE"
                        else:
                            fresh_3.loc[i,"T/F"] = "FALSE"



            fresh_total_bir = len(fresh_2)
            fresh_total_nonbir = len(fresh_3)
            nonfresh_total = len(nonfresh)
            nsd_xx_total = len(nsd_xx)
            rsi_total = len(rsi)
            owb_total = len(owb)
            unknow_total = len(unknow)

            df = pd.DataFrame({  
                "Catogery" :["Fresh BIR","Fresh Non BIR","Non Fresh","Unknow Org","NSD XX","RSI","RR01 Total"],
                "Count" : [fresh_total_bir,fresh_total_nonbir,nonfresh_total,unknow_total,nsd_xx_total,rsi_total,owb_total]
            
            })


            # Write files to in-memory strings using BytesIO
            # See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor
            writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')

            writer.book.filename = output

            sub_file_count = len(mycondition)
            sub_file_total = 0
            for i in range(sub_file_count):
                sub_file = mycondition[i]
                if sub_file == "UNC" or sub_file == "CPN" or sub_file == "TURKEY" or sub_file == "SAVEMART" or sub_file == "IN SCOPE ORG":
                    sub_file_df = owb[owb['Process'] == sub_file ]
                    df = Insert_row(i,df,[mycondition[i], len(sub_file_df)])
                    sub_file_total = sub_file_total + len(sub_file_df)
            
            df = Insert_row(len(df)-1,df,["Total", sub_file_total+fresh_total_bir+fresh_total_nonbir+nonfresh_total+unknow_total+nsd_xx_total+rsi_total])
            df.to_excel(writer, sheet_name='Summary', index=False)


            owb.to_excel(writer, sheet_name="RR01", index=False)
            fresh_2.to_excel(writer, sheet_name="Fresh 02 BIR", index=False)
            fresh_3.to_excel(writer, sheet_name="Fresh 02 Non BIR", index=False)
            nonfresh.to_excel(writer, sheet_name="Non Fresh", index=False)

            sub_file_count = len(mycondition)
            sub_file_total = 0
            for i in range(sub_file_count):
                sub_file = mycondition[i]
                if sub_file == "UNC" or sub_file == "CPN" or sub_file == "TURKEY" or sub_file == "SAVEMART" or sub_file == "IN SCOPE ORG":    
                    sub_file_df = owb[owb['Process'] == sub_file ]
                    sub_file_df.to_excel(writer, sheet_name=sub_file, index=False)

#                   df.insert(i,mycondition[i], len(sub_file_df),True)
#                   sub_file_total = sub_file_total + len(sub_file_df)


            nsd_xx.to_excel(writer, sheet_name="NSD XX", index=False)
            rsi.to_excel(writer, sheet_name="RSI", index=False)
            unknow.to_excel(writer, sheet_name="Unknow Org", index=False)

            writer.save()
            writer.close()
            st.success("Success Completed")
            st.info("Please Click The Download")
            st.download_button(
            label="Download Pre Work File",
            data=output.getvalue(),
            file_name="preworkcompleted.xlsx",
            mime="application/vnd.ms-excel"
            )


            

            consol = consol_1.append(owb)

            # Write files to in-memory strings using BytesIO
            # See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor
            writer_2 = pd.ExcelWriter('pandas_simples.xlsx', engine='xlsxwriter')

            writer_2.book.filename = output_n
            consol.to_excel(writer_2, sheet_name="Data", index=False)

            writer_2.save()
            writer_2.close()
            st.download_button(
            label="Download Consolidated File",
            data=output_n.getvalue(),
            file_name="consolidated.xlsx",
            mime="application/vnd.ms-excel"
            )


    if page == "PreWork Without Consolidated File":

            output = io.BytesIO()
            output_n = io.BytesIO()
            st.subheader("Welcome To PreWork Without Consolidated File")

            
            input_file = st.file_uploader("Upload a CSV OWB File",type=['csv'])
            input_file_2 = st.file_uploader("Upload a XLSX PreWork Condition File",type=['xlsx'])




            if (input_file is not None) and input_file.name.endswith(".csv") and (input_file_2 is not None) and input_file_2.name.endswith(".xlsx") and d != "":


                try:
                    owb1 = pd.read_csv(input_file,converters={'Department Code': lambda x: str(x)}, encoding="unicode_escape")
                except:
                    owb1 = pd.read_csv(input_file,converters={'Department Code': lambda x: str(x)})

                owb_raw = owb1.copy()
                owb1["PreWork Date"]=d
                owb1['Process']=""
                owb1['Consolidated Items'] = ""

                owb1['Best Received External Description'] = owb1['Best Received External Description'].fillna(0)

                row_count = len(owb1)

                #--------------------------------------------------------------------------

                outlet = pd.read_excel(input_file_2, sheet_name = "outlet")
                bir = pd.read_excel(input_file_2, sheet_name = "bir")


                #owb1['Outlet'] = ""

                owb2 = pd.merge(owb1,outlet, on='Processing Group Code', how='left')
                owb = pd.merge(owb2,bir,on='Processing Group Code', how='left')

                owb['Outlet'] = owb['Outlet'].fillna(0)               
                owb['BIR'] = owb['BIR'].fillna("NA")


                #--------------------------------------------------------------------------

                con_df = pd.read_excel(input_file_2,sheet_name="Sub_Group")

                mycondition_1 = list(con_df["Sub_Group_Name"])
                mycondition = []

                for i in range(len(mycondition_1)):
                    txt_1 = mycondition_1[i]
                    txt = str(txt_1).upper()
                    if (txt not in mycondition):
                        mycondition.append(txt)


                #--------------------------------------------------------------------------


                pw = pd.read_excel(input_file_2, sheet_name = "equal")

                pw_row_count = len(pw)

                mycondition_count = len(mycondition)

                for i in range(mycondition_count):
                    con_word_1 = mycondition[i]
                    con_word = str(con_word_1).upper()
                
                    
                    mycondition_n = []
                    for i in range(pw_row_count):
                        txt = pw.loc[i,"Process"]
                        txt2 = pw.loc[i,"Key Words"]
                        if txt.upper() == con_word:
                            mycondition_n.append(txt2)



                    mycondition_n_count = len(mycondition_n)

                    for j in range(mycondition_n_count):
                        mycondition_txt = mycondition_n[j]
                        for i in range(row_count):
                            if con_word == "SAVEMART":
                                txt = owb.loc[i,'Processing Group Code']
                                if str(mycondition_txt).upper() == str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                        owb.loc[i,'Process'] = con_word
                            elif con_word == "IN SCOPE ORG":
                                txt = owb.loc[i,'Processing Group Code']
                                if str(mycondition_txt).upper() in str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                        owb.loc[i,'Process'] = con_word

                            elif con_word=="UNC" or con_word=="CPN" or con_word=="TURKEY" or con_word=="SAVEMART":
                                txt = owb.loc[i,'Best Received External Description']
                                if str(mycondition_txt).upper() == str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                        owb.loc[i,'Process'] = con_word
                            else:
                                txt = owb.loc[i,'Best Received External Description']
                                if str(mycondition_txt).upper() == str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0 and owb.loc[i,'Consolidated Items']=="":
                                        owb.loc[i,'Consolidated Items'] = con_word



                #----------------------------------------------------------------

                pw = pd.read_excel(input_file_2, sheet_name = "contain")

                pw_row_count = len(pw)

                mycondition_count = len(mycondition)

                for i in range(mycondition_count):
                    
                    con_word_1 = mycondition[i]
                    con_word = str(con_word_1).upper()
                    

                    mycondition_n = []
                    for i in range(pw_row_count):
                        txt = pw.loc[i,"Process"]
                        txt2 = pw.loc[i,"Key Words"]
                        if txt.upper() == con_word:
                            mycondition_n.append(txt2)



                    mycondition_n_count = len(mycondition_n)

                    for j in range(mycondition_n_count):
                        mycondition_txt = mycondition_n[j]
                        for i in range(row_count):
                            if con_word == "SAVEMART":
                                txt = owb.loc[i,'Processing Group Code']
                                if str(mycondition_txt).upper() in str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                        owb.loc[i,'Process'] = con_word

                            elif con_word == "IN SCOPE ORG":
                                txt = owb.loc[i,'Processing Group Code']
                                if str(mycondition_txt).upper() in str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                        owb.loc[i,'Process'] = con_word
                            elif con_word=="UNC" or con_word=="CPN" or con_word=="TURKEY" or con_word=="SAVEMART":

                                txt = owb.loc[i,'Best Received External Description']
                                if str(mycondition_txt).upper() in str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0:
                                        owb.loc[i,'Process'] = con_word
                            else:
                                txt = owb.loc[i,'Best Received External Description']
                                if str(mycondition_txt).upper() in str(txt).upper():
                                    if owb.loc[i,'Process'] == "" and owb.loc[i,'Outlet'] != 0 and owb.loc[i,'Consolidated Items']=="":
                                        owb.loc[i,'Consolidated Items'] = con_word

                for i in range(row_count):
                    txt = owb.loc[i,'External Code']
                    txt2 = owb.loc[i,'Process']
                    txt3 = owb.loc[i,"Outlet"]
                    nsd = txt[0:2]

                    if nsd == "XX" and txt2 == "":
                        owb.loc[i,'Process'] = "NSD XX"



                for i in range(row_count):
                    txt = owb.loc[i,'External Code']
                    txt2 = owb.loc[i,'Process']
                    txt3 = owb.loc[i,"Outlet"]

                    if txt[0:3] == "'02" and txt2 == "" and  txt3 == "FOOD":
                        owb.loc[i,'Process'] = "Fresh 02"

                for i in range(row_count):
                    txt = owb.loc[i,'External Code']
                    txt2 = owb.loc[i,'Process']
                    txt3 = owb.loc[i,"Outlet"]

                    if txt[0:3] == "'02" and txt2 == "" and  txt3 == "CONV":
                        owb.loc[i,'Process'] = "Fresh 02"


                for i in range(row_count):
                    txt = owb.loc[i,'External Code']
                    txt2 = owb.loc[i,'Process']
                    txt3 = owb.loc[i,"Outlet"]
                    nsd = txt[0:2]

                    if txt2 == "" and txt3 != 0 and nsd != "XX":
                        owb.loc[i,'Process'] = "Non Fresh"

                for i in range(row_count):
                    txt = owb.loc[i,'Processing Group Description']
                    txt2 = owb.loc[i,'Process']
                    txt3 = owb.loc[i,"Outlet"]
                    rsi = txt[-4:]

                    if txt3 != "RSI" and rsi == " RSI":
                        owb.loc[i,'Process'] = "RSI"
                        owb.loc[i,'Outlet'] = "RSI"

                owb["Set"] = prework_set

                #for i in range(row_count):
                #    txt = owb.loc[i,'External Code']
                #    txt2 = owb.loc[i,'Process']
                #    txt3 = owb.loc[i,"Outlet"]
                #    
                #    if txt[0:3] == "'04" and txt2 == "" and txt3 != "":
                #        owb.loc[i,'Process'] = "Non Fresh"


                #owb.to_csv("new_owb.csv")


                fresh = owb[owb['Process'] == "Fresh 02"]
                nonfresh = owb[owb['Process'] == "Non Fresh"]
                nsd_xx = owb[owb['Process']=="NSD XX"]
                rsi = owb[owb['Outlet']=="RSI"]
                unknow = owb[owb['Outlet'] == 0]

                fresh_row = len(fresh)
                fresh["CONCATENATE"]=""
                fresh["T/F"]=""

                fresh.reset_index(drop=True, inplace=True)

                fresh_row = len(fresh)
                for i in range(fresh_row):
                    txt1 = str(fresh.loc[i,"BIR"])
                    txt2 = str(fresh.loc[i,con1])
                    txt3 = str(fresh.loc[i,con2])
                    txt4 = str(fresh.loc[i,con3])
                    t1 = txt2.replace(" ","")
                    t2 = txt3.replace(" ","")
                    t3 = txt4.replace(" ","")

                    txt5 = t1+t2+t3


                    fresh.loc[i,"CONCATENATE"] = txt5

                
                fresh_bir = fresh[fresh['BIR'] != "NA"]
                fresh_nonbir = fresh[fresh['BIR'] == "NA"]

                fresh_bir = fresh_bir.sort_values('CONCATENATE', ascending=False)
                con_table = fresh_bir.groupby(['CONCATENATE'])['External Code'].count().reset_index()
                con_table.rename({'External Code':'Count If'}, axis=1, inplace=True)
                con_table["Unique Number"] = ""

                con_table_row = len(con_table)

                for i in range(con_table_row):
                    if i < con_table_row:
                        con_table.loc[i,"Unique Number"] = i+1
                    
                fresh_2 = pd.merge(fresh_bir,con_table, on='CONCATENATE', how='right')

                fresh_2.reset_index(drop=True, inplace=True)
                fresh_row_bir = len(fresh_2)
                for i in range(fresh_row_bir):
                    if i < fresh_row_bir-1: 
                        j = i+1

                        txt1 = fresh_2.loc[i,"CONCATENATE"]
                        txt2 = fresh_2.loc[j,"CONCATENATE"]
                        if txt1 != "":
                            if txt1 == txt2:
                                fresh_2.loc[i,"T/F"] = "TRUE"
                            else:
                                fresh_2.loc[i,"T/F"] = "FALSE"

                fresh_nonbir = fresh_nonbir.sort_values('CONCATENATE', ascending=False)
                con_table = fresh_nonbir.groupby(['CONCATENATE'])['External Code'].count().reset_index()
                con_table.rename({'External Code':'Count If'}, axis=1, inplace=True)
                con_table["Unique Number"] = ""

                con_table_row = len(con_table)

                for i in range(con_table_row):
                    if i < con_table_row:
                        con_table.loc[i,"Unique Number"] = i+1

                fresh_3 = pd.merge(fresh_nonbir,con_table, on='CONCATENATE', how='right')

                fresh_3.reset_index(drop=True, inplace=True)
                fresh_row_nonbir = len(fresh_3)
                for i in range(fresh_row_nonbir):
                    if i < fresh_row_nonbir-1: 
                        j = i+1

                        txt1 = fresh_3.loc[i,"CONCATENATE"]
                        txt2 = fresh_3.loc[j,"CONCATENATE"]
                        if txt1 != "":
                            if txt1 == txt2:
                                fresh_3.loc[i,"T/F"] = "TRUE"
                            else:
                                fresh_3.loc[i,"T/F"] = "FALSE"



                fresh_total_bir = len(fresh_2)
                fresh_total_nonbir = len(fresh_3)
                nonfresh_total = len(nonfresh)
                nsd_xx_total = len(nsd_xx)
                rsi_total = len(rsi)
                owb_total = len(owb)
                unknow_total = len(unknow)

                df = pd.DataFrame({  
                    "Catogery" :["Fresh BIR","Fresh Non BIR","Non Fresh","Unknow Org","NSD XX","RSI","RR01 Total"],
                    "Count" : [fresh_total_bir,fresh_total_nonbir,nonfresh_total,unknow_total,nsd_xx_total,rsi_total,owb_total]
                
                })


                # Write files to in-memory strings using BytesIO
                # See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor
                writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')

                writer.book.filename = output

                sub_file_count = len(mycondition)
                sub_file_total = 0
                for i in range(sub_file_count):
                    sub_file = mycondition[i]
                    if sub_file == "UNC" or sub_file == "CPN" or sub_file == "TURKEY" or sub_file == "SAVEMART" or sub_file == "IN SCOPE ORG":
                        sub_file_df = owb[owb['Process'] == sub_file ]
                        df = Insert_row(i,df,[mycondition[i], len(sub_file_df)])
                        sub_file_total = sub_file_total + len(sub_file_df)
                
                df = Insert_row(len(df)-1,df,["Total", sub_file_total+fresh_total_bir+fresh_total_nonbir+nonfresh_total+unknow_total+nsd_xx_total+rsi_total])
                df.to_excel(writer, sheet_name='Summary', index=False)


                owb.to_excel(writer, sheet_name="RR01", index=False)
                fresh_2.to_excel(writer, sheet_name="Fresh 02 BIR", index=False)
                fresh_3.to_excel(writer, sheet_name="Fresh 02 Non BIR", index=False)
                nonfresh.to_excel(writer, sheet_name="Non Fresh", index=False)

                sub_file_count = len(mycondition)
                sub_file_total = 0
                for i in range(sub_file_count):
                    sub_file = mycondition[i]
                    if sub_file == "UNC" or sub_file == "CPN" or sub_file == "TURKEY" or sub_file == "SAVEMART" or sub_file == "IN SCOPE ORG":    
                        sub_file_df = owb[owb['Process'] == sub_file ]
                        sub_file_df.to_excel(writer, sheet_name=sub_file, index=False)

#                   df.insert(i,mycondition[i], len(sub_file_df),True)
#                   sub_file_total = sub_file_total + len(sub_file_df)


                nsd_xx.to_excel(writer, sheet_name="NSD XX", index=False)
                rsi.to_excel(writer, sheet_name="RSI", index=False)
                unknow.to_excel(writer, sheet_name="Unknow Org", index=False)

                writer.save()
                writer.close()
                st.success("Success Completed")
                st.info("Please Click The Download")
                st.download_button(
                label="Download Pre Work File",
                data=output.getvalue(),
                file_name="preworkcompleted.xlsx",
                mime="application/vnd.ms-excel"
                )

                

                # Write files to in-memory strings using BytesIO
                # See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor
                writer_2 = pd.ExcelWriter('pandas_simples.xlsx', engine='xlsxwriter')
                
                writer_2.book.filename = output_n

                owb.to_excel(writer_2, sheet_name="Data", index=False)

                writer_2.save()
                writer_2.close()
                st.download_button(
                label="Download Consolidated File",
                data=output_n.getvalue(),
                file_name="consolidated.xlsx",
                mime="application/vnd.ms-excel"
                )
                



    if page == "PreWork Fresh Allocation":

            output = io.BytesIO()
            st.subheader("Welcome To PreWork Fresh Allocation")

            
            input_file = st.file_uploader("Upload a CSV OWB File",type=['csv'])
            input_file_2 = st.file_uploader("Upload a XLSX PreWork Condition File",type=['xlsx'])

            if (input_file is not None) and input_file.name.endswith(".csv") and (input_file_2 is not None) and input_file_2.name.endswith(".xlsx"):


                try:
                    owb1 = pd.read_csv(input_file,converters={'Department Code': lambda x: str(x)}, encoding="unicode_escape")
                except:
                    owb1 = pd.read_csv(input_file,converters={'Department Code': lambda x: str(x)})
                    
                row_count = len(owb1)

                owb1["Process"] = ""

                #--------------------------------------------------------------------------
                
                    
                outlet = pd.read_excel(input_file_2, sheet_name = "outlet")
                bir = pd.read_excel(input_file_2, sheet_name = "bir")
                
                allocation_list = pd.read_excel(input_file_2,sheet_name="allocation_list")


                
                #owb1['Outlet'] = ""

                owb2 = pd.merge(owb1,outlet, on='Processing Group Code', how='left')
                owb = pd.merge(owb2,bir,on='Processing Group Code', how='left')
                owb['Outlet'] = owb['Outlet'].fillna(0) 
                owb['BIR'] = owb['BIR'].fillna("NA")


                
                #--------------------------------------------------------------------------



                owb_row = len(owb)
                owb["CONCATENATE"]=""
                owb["T/F"]=""

                owb.reset_index(drop=True, inplace=True)

                owb_row = len(owb)
                for i in range(owb_row):
                    txt1 = str(owb.loc[i,"BIR"])
                    txt2 = str(owb.loc[i,con1])
                    txt3 = str(owb.loc[i,con2])
                    txt4 = str(owb.loc[i,con3])
                    t1 = txt2.replace(" ","")
                    t2 = txt3.replace(" ","")
                    t3 = txt4.replace(" ","")

                    txt5 = t1+t2+t3


                    owb.loc[i,"CONCATENATE"] = txt5

                
                fresh_bir = owb[owb['BIR'] != "NA"]
                fresh_nonbir = owb[owb['BIR'] == "NA"]

                fresh_bir = fresh_bir.sort_values('CONCATENATE', ascending=False)
                con_table = fresh_bir.groupby(['CONCATENATE'])['External Code'].count().reset_index()
                con_table.rename({'External Code':'Count If'}, axis=1, inplace=True)
                con_table["Unique Number"] = ""

                con_table_row = len(con_table)

                for i in range(con_table_row):
                    if i < con_table_row:
                        con_table.loc[i,"Unique Number"] = "A"+str(i+1)


                fresh_2 = pd.merge(fresh_bir,con_table, on='CONCATENATE', how='right')

                fresh_2.reset_index(drop=True, inplace=True)
                fresh_row_bir = len(fresh_2)
                for i in range(fresh_row_bir):
                    if i < fresh_row_bir-1: 
                        j = i+1

                        txt1 = fresh_2.loc[i,"CONCATENATE"]
                        txt2 = fresh_2.loc[j,"CONCATENATE"]
                        if txt1 != "":
                            if txt1 == txt2:
                                fresh_2.loc[i,"T/F"] = "TRUE"
                            else:
                                fresh_2.loc[i,"T/F"] = "FALSE"

                fresh_nonbir = fresh_nonbir.sort_values('CONCATENATE', ascending=False)
                con_table = fresh_nonbir.groupby(['CONCATENATE'])['External Code'].count().reset_index()
                con_table.rename({'External Code':'Count If'}, axis=1, inplace=True)
                con_table["Unique Number"] = ""

                con_table_row = len(con_table)

                for i in range(con_table_row):
                    if i < con_table_row:
                        con_table.loc[i,"Unique Number"] = "B"+str(i+1)

                fresh_3 = pd.merge(fresh_nonbir,con_table, on='CONCATENATE', how='right')

                fresh_3.reset_index(drop=True, inplace=True)
                fresh_row_nonbir = len(fresh_3) 
                for i in range(fresh_row_nonbir):
                    if i < fresh_row_nonbir-1: 
                        j = i+1

                        txt1 = fresh_3.loc[i,"CONCATENATE"]
                        txt2 = fresh_3.loc[j,"CONCATENATE"]
                        if txt1 != "":
                            if txt1 == txt2:
                                fresh_3.loc[i,"T/F"] = "TRUE"
                            else:
                                fresh_3.loc[i,"T/F"] = "FALSE"



                fresh_bir_total = len(fresh_2)
                fresh_nonbir_total = len(fresh_3)
                
                owb_total = len(owb)
            

                df = pd.DataFrame({
                    "Fresh BIR" : [fresh_bir_total],
                    "Fresh Non BIR" : [fresh_nonbir_total],

                    "Total" : [fresh_bir_total+fresh_nonbir_total],
                    "RR01 Total": [owb_total]

                })

                allocation_name = list(allocation_list["allocation_name"])
                allocation_type = list(allocation_list["allocation_type"])
                target = list(allocation_list["target"])
                allocation_tool = list(allocation_list["allocation_tool"])
                
                total_target = allocation_list["target"].sum()


                allocation_table_1 = fresh_2.groupby(['Unique Number'])['Count If'].count().reset_index()

                allocation_table_2 = fresh_3.groupby(['Unique Number'])['Count If'].count().reset_index()

                allocation_table = allocation_table_1.append(allocation_table_2)
                allocation_table = allocation_table.sort_values(by=['Count If','Unique Number'], ascending=False)
                allocation_table.reset_index(drop=True, inplace=True)
                allocation_table["allocation_name"] = "NA"
                allocation_table["allocation_tool"] = "NA"

                total_allocation_3 = allocation_table[allocation_table["allocation_name"] != "NA"]
                total_allocation = len(total_allocation_3)
                
                m = 0.1
                j = 0
                i = 0
                n = 0
                j2 = 0
                upt = "no"

                if total_target>0:

                    while i < len(allocation_table) and total_allocation < len(allocation_table):

                        if j==len(allocation_name) and n+1==i:
                            j=0
                        elif len(allocation_name)==1 and i != len(allocation_table)-1:
                            i = i+1
                        
                        else:        
                            if j>1 and i==n+1 and upt == "yes":
                                m = j-2
                                upt = "no"
                            elif j==1 and i==n+1 and upt == "yes":
                                m = 0
                                upt = "no"

                        n = i
                        nm = allocation_table.loc[i,"allocation_name"]
                        dup = allocation_table.loc[i,"Count If"]

                        if nm == "NA":

                            total_allocation_1 = allocation_table[allocation_table["allocation_name"] != "NA"]
                            total_allocation = len(total_allocation_1)
                            if total_allocation < len(allocation_table):
                                if j < len(allocation_name):
                                    
                                    associate_name_1 = allocation_name[j]
                                    associate_name = str(associate_name_1).upper()
                                    al_type = allocation_type[j]
                                    al_target = target[j]
                                    al_tool = allocation_tool[j]
                                    
                                    try:
                                        grp_1 = allocation_table.groupby(['allocation_name'])["Count If"].count().reset_index()
                                        grp_2 = grp_1[grp_1["allocation_name"]==associate_name]
                                        grp = list(grp_2["Count If"])
                                        #pr_al_1 = pre_allocation_1[pre_allocation_1["allocation_name"]==associate_name]
                                        #pr_al = list(pr_al_1["Count If"])
                                        actual_count = grp[0] #+pr_al[0]
                                    except:
                                        actual_count = 0

                                    if actual_count < al_target:
                                        if dup>1 and al_type=="Including_Duplicate":
                                            allocation_table.loc[i,"allocation_name"] = associate_name
                                            allocation_table.loc[i,"allocation_tool"] = al_tool
                                            
                                            j=j+1
                                            i=i+1
                                            upt = "yes"
                                        elif dup==1 and al_type=="Including_Duplicate":
                                            allocation_table.loc[i,"allocation_name"] = associate_name
                                            allocation_table.loc[i,"allocation_tool"] = al_tool

                                            j=j+1
                                            i=i+1
                                            upt = "yes"
                                        elif dup==1 and al_type=="Unique":
                                            allocation_table.loc[i,"allocation_name"] = associate_name
                                            allocation_table.loc[i,"allocation_tool"] = al_tool

                                            j=j+1
                                            i=i+1
                                            upt = "yes"
                                        elif j==len(allocation_name)-1 and i != len(allocation_table):
                                            j=0
                                        elif m==j:
                                            j = j+1
                                            i = i+1
                                        else:
                                            j=j+1
                                    elif j==len(allocation_name)-1:
                                        j = 0
                                    elif m==j:
                                        j = j+1
                                        i = i+1
                                    else:
                                        j=j+1
                                else:
                                    i=i+1
                            else:
                                i = i+len(allocation_table)
                        else:
                            i = i+1
                        
                        if len(allocation_name)==1 and i == len(allocation_table)-1:
                            i = i+1


                allocation_table_4 = allocation_table[["Unique Number","allocation_name","allocation_tool"]]
                df1 = pd.merge(fresh_2,allocation_table_4,on="Unique Number",how="left")
                df2 = pd.merge(fresh_3,allocation_table_4,on="Unique Number",how="left")

                pre_allocation = allocation_table.groupby(["allocation_name"])["Count If"].count().reset_index()
                allocated = pre_allocation.groupby(["allocation_name"])["Count If"].sum().reset_index()

                pre_allocation_list = pd.read_excel(input_file_2, sheet_name = "allocation_list")
                
                count_nan = pre_allocation_list["total_allocated_count"].isna().sum()
                
                if count_nan>0:
                    pre_allocation_list["total_allocated_count"]=pre_allocation_list["total_allocated_count"].fillna(0)

                i = 0
                while i < len(allocated):
                    name_1 = allocated.loc[i,"allocation_name"]
                    count_m = allocated.loc[i,"Count If"]

                    j = 0
                    while j<len(pre_allocation_list):
                        name_3 = pre_allocation_list.loc[j,"allocation_name"]
                        name_2 = str(name_3).upper()

                        if name_1 == name_2:

                            count_n = pre_allocation_list.loc[j,"total_allocated_count"]
                            pre_allocation_list.loc[j,"total_allocated_count"] = count_n + count_m
                            pre_allocation_list.loc[j,"allocated_count"] = count_m
                            

                        j = j+1
                    
                    i = i+1
                
                ogrds_1 = df1[['Exception Type','External Code','Seq','Processing Group Code','Processing Group Description','Best Received External Description','Best Existing External Description','Department Description','Supplier Description','Impact','Price','Current Assignment Description','Country Current Assignment Description','External Item/Predicted PG/CI','External Item/Predicted Product Class','Outlet','BIR','CONCATENATE','T/F','Count If','Unique Number','allocation_name','allocation_tool']]
                ogrds_2 = df2[['Exception Type','External Code','Seq','Processing Group Code','Processing Group Description','Best Received External Description','Best Existing External Description','Department Description','Supplier Description','Impact','Price','Current Assignment Description','Country Current Assignment Description','External Item/Predicted PG/CI','External Item/Predicted Product Class','Outlet','BIR','CONCATENATE','T/F','Count If','Unique Number','allocation_name','allocation_tool']]
                ogrds_2 = ogrds_2.append(ogrds_1)

                ogrds = ogrds_2[ogrds_2["allocation_tool"]=="OGRDS"]
                ogrds["GIC"] = ""
                ogrds["User Action"] = ""
                ogrds["CG"] = ""
                ogrds["Comments"] = ""
                


                # Write files to in-memory strings using BytesIO
                # See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor
                writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')

                writer.book.filename = output


                df.to_excel(writer, sheet_name='Summary', index=False)
                owb.to_excel(writer, sheet_name="RR01", index=False)
                df1.to_excel(writer, sheet_name="Fresh BIR", index=False)
                df2.to_excel(writer, sheet_name="Fresh Non BIR", index=False)
                ogrds.to_excel(writer, sheet_name="OGRDS Allocation", index=False)
                
                pre_allocation_list.to_excel(writer, sheet_name="allocation_list", index=False)
                
                




                writer.save()
                writer.close()
                st.success("Success Completed")
                st.info("Please Click The Download")
                st.download_button(
                label="Download Pre Work File",
                data=output.getvalue(),
                file_name="preworkcompleted.xlsx",
                mime="application/vnd.ms-excel"
                )
                st.dataframe(df)

#!/usr/bin/env python
# coding: utf-8

##Calculating Piotroski's F score
import numpy as np
import pandas as pd
from tabula import read_pdf as rp
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import sys
import argparse

## setting up browser ##returns driver
def browser_setup():
    url="https://www.moneycontrol.com/stocksmarketsindia/"
    chrome_options = Options();
    chrome_options.add_argument('--window-size=1920,1080');
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),options=chrome_options)  
    driver.get(url)
    driver.implicitly_wait(5)
    print("driver loaded")
    return driver


##Loading excel to connect security ticker to bse code
def sec_id(bse_scripts,security_ticker):
    sheet=pd.read_csv(bse_scripts);
    row=sheet[sheet["Security Id"]==security_ticker]
    if(row.shape[0]==0):
        code = "Invalid Ticker"
        print(code);
        sys.exit("Please enter a valid BSE Ticker");
    else:
        code = row.iloc[0,0];
        return code;



##Download list of securities for the day from https://www.bseindia.com/corporates/List_Scrips.aspx and save it in the folder with the py file


#to put security's bse code in search bar and open its page
def gotosecurity(code,driver):
    search_bar = driver.find_element_by_xpath('/html/body/header/div[1]/div/div[2]/div[2]/div[1]/div/form/input[5]')
    search_bar.clear()
    search_bar.send_keys(str(code));
    go = driver.find_element_by_xpath('/html/body/header/div[1]/div/div[2]/div[2]/div[1]/a')
    go.click();
    time.sleep(5);
    print("Opened security page")


##get links to financial statements
def getlinks(driver):
    financials=driver.find_element_by_xpath('//*[@id="sec_quotes"]/div[2]/div/div[1]/div[3]/div/div/nav/div/ul/li[8]/a')
    financials.click();
    time.sleep(5);
    bs= driver.find_element_by_xpath('//*[@id="sec_quotes"]/div[2]/div/div[1]/div[3]/div/div/nav/div/ul/li[8]/ul/li[1]/a')
    bs_link=bs.get_attribute("href");
    pnl= driver.find_element_by_xpath('//*[@id="sec_quotes"]/div[2]/div/div[1]/div[3]/div/div/nav/div/ul/li[8]/ul/li[2]/a')
    pnl_link = pnl.get_attribute("href");
    cf= driver.find_element_by_xpath('//*[@id="sec_quotes"]/div[2]/div/div[1]/div[3]/div/div/nav/div/ul/li[8]/ul/li[7]/a')
    cf_link = cf.get_attribute("href")
    yr= driver.find_element_by_xpath('//*[@id="sec_quotes"]/div[2]/div/div[1]/div[3]/div/div/nav/div/ul/li[8]/ul/li[6]/a')
    yr_link = yr.get_attribute("href")
    statement_links = [bs_link,pnl_link,cf_link,yr_link];
    print("extracted_links");
    return statement_links;


def getbs(driver,bs_link):
    driver.get(bs_link);
    time.sleep(5);
    values=pd.DataFrame();
    for body in driver.find_elements_by_xpath('//*[@id="standalone-new"]/div[1]/table/tbody'):
            for r in body.find_elements_by_xpath('./tr'):
                val=pd.DataFrame();
                for data in r.find_elements_by_xpath('./td'):
                    val=val.append([data.get_attribute('textContent')],ignore_index=True);
                values=values.append(val.T,ignore_index=True)
    return values   


def getpnl(driver,pnl_link):
    driver.get(pnl_link);
    time.sleep(5);
    values=pd.DataFrame();
    for body in driver.find_elements_by_xpath('//*[@id="standalone-new"]/div[1]/table/tbody'):
            for r in body.find_elements_by_xpath('./tr'):
                val=pd.DataFrame();
                for data in r.find_elements_by_xpath('./td'):
                    val=val.append([data.get_attribute('textContent')],ignore_index=True);
                values=values.append(val.T,ignore_index=True)
    return values 



def getcf(driver,cf_link):
    driver.get(cf_link);
    time.sleep(5);
    values=pd.DataFrame();
    for body in driver.find_elements_by_xpath('//*[@id="standalone-new"]/div[1]/table/tbody'):
            for r in body.find_elements_by_xpath('./tr'):
                val=pd.DataFrame();
                for data in r.find_elements_by_xpath('./td'):
                    val=val.append([data.get_attribute('textContent')],ignore_index=True);
                values=values.append(val.T,ignore_index=True)
    return values    



def getyr(driver,yr_link):
    driver.get(yr_link);
    time.sleep(5);
    values=pd.DataFrame();
    for body in driver.find_elements_by_xpath('//*[@id="standalone-new"]/div[1]/table/tbody'):
            for r in body.find_elements_by_xpath('./tr'):
                val=pd.DataFrame();
                for data in r.find_elements_by_xpath('./td'):
                    val=val.append([data.get_attribute('textContent')],ignore_index=True);
                values=values.append(val.T,ignore_index=True)
    for i in range(values.shape[0]):
        for j in reversed(range(values.shape[1]-1)):
            if(values.iloc[i,j]=="--"):
                values.iloc[i,j]=values.iloc[i,j+1]
    return values    



def get_statements(security_ticker,bse_scripts):
    security_ticker=security_ticker.upper()
    code = sec_id(bse_scripts,security_ticker);
    driver=browser_setup();
    gotosecurity(code,driver); #Opens security page in driver
    statement_links=getlinks(driver);
    bs=getbs(driver,statement_links[0]);
    pnl=getpnl(driver,statement_links[1]);
    cf= getcf(driver,statement_links[2]);
    yr = getyr(driver,statement_links[3]);
##remove repeated column from financial statements ## exists in case of multiple data/filings for latest year
    for i in reversed(range(1,bs.shape[1])):
        if(bs.iloc[0,i]==bs.iloc[0,i-1]):
            bs.loc[bs[i-1]=="0.00",i-1]=bs[bs[i-1]=="0.00"][i]
            bs=bs.drop(labels=i,axis=1);
            bs.columns=range(bs.shape[1]);
    
    for i in reversed(range(1,pnl.shape[1])):
        if(pnl.iloc[0,i]==pnl.iloc[0,i-1]):
            pnl.loc[pnl[i-1]=="0.00",i-1]=pnl[pnl[i-1]=="0.00"][i]
            pnl=pnl.drop(labels=i,axis=1);
            pnl.columns=range(pnl.shape[1]);
    
    for i in reversed(range(1,cf.shape[1])):
        if(cf.iloc[0,i]==cf.iloc[0,i-1]):
            cf.loc[cf[i-1]=="0.00",i-1]=cf[cf[i-1]=="0.00"][i]
            cf=cf.drop(labels=i,axis=1);
            cf.columns=range(cf.shape[1]);
            
    for i in reversed(range(1,yr.shape[1])):
        if(yr.iloc[0,i]==yr.iloc[0,i-1]):
            yr.loc[yr[i-1]=="0.00",i-1]=yr[yr[i-1]=="0.00"][i]
            yr=yr.drop(labels=i,axis=1);
            yr.columns=range(yr.shape[1]);
    print("extracted statements\n")
    statements=[bs,pnl,cf,yr];
    return statements;


################ Get financial Statements upto here #####################################


##Defining required variables for Pietroskei ratios
def pet_rat(bs,pnl,cf,yr):
    TA_0=float(bs[bs[0]=="Total Assets"].iloc[0,1].replace(',','')) ##Total Assets
    TA_1=float(bs[bs[0]=="Total Assets"].iloc[0,2].replace(',','')) ##Previous Year's Total Assets
    TA_2=float(bs[bs[0]=="Total Assets"].iloc[0,3].replace(',','')) ##Previous to Previous Year's Total Assets
    NI_0=float(pnl[pnl[0].isin(["Profit/Loss For The Period","Net Profit / Loss for The Year"])].iloc[0,1].replace(',','')) ##Net income
    NI_1=float(pnl[pnl[0].isin(["Profit/Loss For The Period","Net Profit / Loss for The Year"])].iloc[0,2].replace(',','')) ##Previous Year's Total Assets
#average total assets
    avg_ta_0 = np.mean([TA_0,TA_1]);
    avg_ta_1 = np.mean([TA_1,TA_2]);
#Operating Cash flow
    ocf = float(cf[cf[0]=="Net CashFlow From Operating Activities"].iloc[0,1].replace(',','')) 
#Long term debt
    ltd_0 = float(bs[bs[0].isin(["Long Term Borrowings","Borrowings"])].iloc[0,1].replace(',',''))
    ltd_1 = float(bs[bs[0].isin(["Long Term Borrowings","Borrowings"])].iloc[0,2].replace(',',''))
#Equity issued in a year
    if(yr[yr[0]=="No Of Shares (Crores)"].iloc[0,1].replace(',','')=="\xa0"): #setting values to zero if empty
        yr.loc[yr[0]=="No Of Shares (Crores)",1:]="0"
    eq_0 = float(yr[yr[0]=="No Of Shares (Crores)"].iloc[0,1].replace(',',''));
    eq_1 = float(yr[yr[0]=="No Of Shares (Crores)"].iloc[0,2].replace(',',''));
#current assets for banks and other firms
    if("Cash and Balances with Reserve Bank of India" in bs[0].values): ##banks
        cb_with_rbi_0 = float(bs[bs[0]=="Cash and Balances with Reserve Bank of India"].iloc[0,1].replace(',',''));
        cb_with_rbi_1 = float(bs[bs[0]=="Cash and Balances with Reserve Bank of India"].iloc[0,2].replace(',',''));
        bal_with_banks_0=float(bs[bs[0]=="Balances with Banks Money at Call and Short Notice"].iloc[0,1].replace(',',''));
        bal_with_banks_1=float(bs[bs[0]=="Balances with Banks Money at Call and Short Notice"].iloc[0,2].replace(',',''));
        investments_0= float(bs[bs[0]=="Investments"].iloc[0,1].replace(',',''));
        investments_1= float(bs[bs[0]=="Investments"].iloc[0,2].replace(',',''));
        advances_0 = float(bs[bs[0]=="Advances"].iloc[0,1].replace(',',''));
        advances_1 = float(bs[bs[0]=="Advances"].iloc[0,2].replace(',',''));
        curr_ass_0 = cb_with_rbi_0 + bal_with_banks_0 + investments_0 + advances_0;
        curr_ass_1 = cb_with_rbi_1 + bal_with_banks_1 + investments_1 + advances_1;
    ##taking borrwings as short term borrowings for banks
        deposits_0 =   float(bs[bs[0]=="Deposits"].iloc[0,1].replace(',',''));
        deposits_1 =   float(bs[bs[0]=="Deposits"].iloc[0,2].replace(',',''));
        borrowings_0 = ltd_0;
        borrowings_1 = ltd_1;
        ltd_0=0;
        ltd_1=0;
        curr_liab_0 = deposits_0+borrowings_0;
        curr_liab_1 = deposits_1+borrowings_1;
        revenue_gross_0 = float(pnl[pnl[0]=="Total Interest Earned"].iloc[0,1].replace(',',''));
        revenue_gross_1 = float(pnl[pnl[0]=="Total Interest Earned"].iloc[0,2].replace(',',''));
        gross_expenses_0= float(pnl[pnl[0]=="Total Operating Expenses"].iloc[0,1].replace(',',''));
        gross_expenses_1= float(pnl[pnl[0]=="Total Operating Expenses"].iloc[0,2].replace(',',''));
    else:
        revenue_gross_0 = float(pnl[pnl[0]=="Revenue From Operations [Gross]"].iloc[0,1].replace(',',''));
        revenue_gross_1 = float(pnl[pnl[0]=="Revenue From Operations [Gross]"].iloc[0,2].replace(',',''));
        material_expenses_0= float(pnl[pnl[0]=="Cost Of Materials Consumed"].iloc[0,1].replace(',',''));
        material_expenses_1= float(pnl[pnl[0]=="Cost Of Materials Consumed"].iloc[0,2].replace(',',''));
        labor_expenses_0 = float(pnl[pnl[0]=="Employee Benefit Expenses"].iloc[0,1].replace(',',''));
        labor_expenses_1 = float(pnl[pnl[0]=="Employee Benefit Expenses"].iloc[0,2].replace(',',''));
        gross_expenses_0 = material_expenses_0-labor_expenses_0;
        gross_expenses_1 = material_expenses_1-labor_expenses_1;
        curr_ass_0 = float(bs[bs[0]=="Total Current Assets"].iloc[0,1].replace(',',''));
        curr_ass_1 = float(bs[bs[0]=="Total Current Assets"].iloc[0,2].replace(',',''));
        curr_liab_0 = float(bs[bs[0]=="Total Current Liabilities"].iloc[0,1].replace(',',''));
        curr_liab_1 = float(bs[bs[0]=="Total Current Liabilities"].iloc[0,2].replace(',',''));
        
        
        
        
    
    
    
    # 1) Profitability ratis
#roa
    roa_0=NI_0/TA_1;
    
    roa_1=NI_1/TA_2;
#cfra = Net cash flow from operating activities/Total Assets from the beginning of the year
    cfra = ocf/TA_1
    
#delta roa
    del_roa=roa_0-roa_1;
    
#accurals net cash flow - net operating income/Total assets from the beginning of the year
    accurals = roa_0-cfra;

# 2) Capital Structure Measures
#delta leverage
    lev_0 = ltd_0/avg_ta_0;
    lev_1 = ltd_1/avg_ta_1;
    del_lev = lev_0-lev_1;
# delta liquidity
    liquidity_0 = curr_ass_0/curr_liab_0;
    liquidity_1 = curr_ass_1/curr_liab_1;
    del_liq = liquidity_0 - liquidity_1;
#del_share_issue
    del_eq = eq_0-eq_1;
# 3) Efficiency Measures
#Delta gross margin
    gross_profit_0 = revenue_gross_0 - gross_expenses_0;
    gross_profit_1 = revenue_gross_1 - gross_expenses_1;
    gross_margin_0 = gross_profit_0/revenue_gross_0;
    gross_margin_1 = gross_profit_1/revenue_gross_1;
    
    del_gross_margin = gross_margin_0-gross_margin_1;
#Delta Asset Turnover
    ass_turn_0 = revenue_gross_0/TA_1;
    ass_turn_1 = revenue_gross_1/TA_2;
    del_ass_turn= ass_turn_0-ass_turn_1;
    #ratios = [roa_0,cfra,del_roa,accurals,del_lev,del_liq,del_eq,del_gross_margin,del_ass_turn];
    ratios = pd.DataFrame({'Category': ['RoA', 'CFRA','Delta RoA','Accurals','Delta Leverage','Delta Liquidity','Equity Issued in year','Delta Gross Margin','Delta Asset Turnover'], 'ratio': [roa_0,cfra,del_roa,accurals,del_lev,del_liq,del_eq,del_gross_margin,del_ass_turn]})
    return ratios;


##Calculating Petroski's ratios

def petroski_ratios(ratios):
# 1) Profitability ratios
#roa
    roa = ratios.iloc[0,1];
    if(roa>0):f_roa=1;
    else: f_roa=0;
#cfra = Net cash flow from operating activities/Total Assets from the beginning of the year
    cfra = ratios.iloc[1,1]
    if(cfra>0):f_cfra=1;
    else:f_cfra=0;
#delta roa
    del_roa=ratios.iloc[2,1];
    if(del_roa>0): f_del_roa=1;
    else: f_del_roa=0;
#accurals net cash flow - net operating income/Total assets from the beginning of the year
    accurals = ratios.iloc[3,1];
    if(accurals>0): f_accurals=0;
    else: f_accurals=1;
    
    f_profit = f_roa+f_cfra+f_del_roa+f_accurals;

# 2) Capital Structure Measures
#delta leverage

    del_lev = ratios.iloc[4,1]
    if(del_lev<0): f_del_lev=1;
    else: f_del_lev=0;
# delta liquidity
    del_liq = ratios.iloc[5,1];
    if(del_liq>0): f_del_liq=1;
    else: f_del_liq=0;
#del_share_issue
    del_eq=ratios.iloc[6,1];
    if(del_eq>0): f_del_eq=0;
    else: f_del_eq=1;
        
    f_cap_struct = f_del_lev+f_del_liq+f_del_eq;

# 3) Efficiency Measures
#Delta gross margin
    del_gross_margin = ratios.iloc[7,1];
    if(del_gross_margin>0): f_del_gross_margin=1;
    else: f_del_gross_margin=0;
#Delta Asset Turnover
    del_ass_turn = ratios.iloc[8,1];
    if(del_ass_turn>0): f_del_ass_turn=1;
    else: f_del_ass_turn=0;
    
    f_efficiency = f_del_gross_margin+f_del_ass_turn;
    f_score = f_roa+f_cfra+f_del_roa+f_accurals+f_del_lev+f_del_liq+f_del_eq+f_del_gross_margin+f_del_ass_turn;
    
    result = pd.DataFrame({'Category': ['Profitability', 'Capital Structure','Efficiency','overall f score'], 'f score': [f_profit,f_cap_struct,f_efficiency,f_score]})
    return result



def calfscore(secticker):
    bse_scripts = input("Address of Select.csv file: ");
    statements=get_statements(secticker,bse_scripts);
    bs=statements[0];
    pnl=statements[1];
    cf= statements[2];
    yr =statements[3];
    ratios=pet_rat(bs,pnl,cf,yr);
    score = petroski_ratios(ratios);
    return [score,ratios]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bse_ticker', type=str, help='mandatory argument')
    args = parser.parse_args()
    
    [fscore,ratios]=calfscore(args.bse_ticker);
    for i,row in fscore.iterrows():
    	print(row['Category'],' - ',row['f score'])
if __name__ == '__main__':
    main()




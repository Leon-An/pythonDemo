import datetime
import xlrd
import np
import numpy
import pymysql
import time


# 打开数据库连接
# 连接数据库


# 使用execute()方法执行sql语句
# cursor.execute('select version()')
# fetchone()方法获取返回对象的单条数据
# data = cursor.fetchone()
# data = cursor.fetchall()
# print('Database version:{0}'.format(data))


def guzhai(datenow):
    # datenow = datenow[1:9]
    d0 = datetime.datetime(1899, 12, 30)
    d1 = datetime.datetime(int(datenow[0:4]), int(datenow[4:6]), int(datenow[6:8]))
    dnow = (d1 - d0).days
    # print('dnow=',dnow)

    workbook = xlrd.open_workbook(r'H://20200507股权质押.xlsx')
    sheet0 = workbook.sheets()[0]  # 读第一个标签
    nrow = sheet0.nrows
    ncol = sheet0.ncols
    # print('行=',nrow,'列=',ncol)
    row = [[]] * nrow

    for i in range(nrow):
        row[i] = sheet0.row_values(i)  # 某一行数据
    row = np.array(row)

    for j in range(7, ncol):
        if dnow >= float(row[0, j]):
            j0 = j
            break

    # connect = pymysql.Connect(
    #     host='47.92.52.147',
    #     port=29782,
    #     user='zhlan',
    #     passwd='@KlQG@DehKyw9ebyx7uQ',
    #     db='fcdb',
    #     charset='utf8'
    # )
    connect = pymysql.Connect(
        host='47.92.52.147',
        port=29782,
        user='dwyang',
        passwd='MuU#bXp_97Ly7N4#',
        db='fcdb',
        charset='utf8'
    )

    # 获取游标
    cursor = connect.cursor()
    # 1 ,4,6,8
    cursor.execute('''select 
                        IFNULL(CR0001_008,0) CR0001_008,
                        ITCODE,
                       ITNAME,
                       COMPCODE2 ,
                       COMPNAME2 ,
                       COMPCODE3 ,
                       COMPNAME3 ,
                       COMPCODE4 ,
                       COMPNAME4
                from (
                         select A.*,
                                CR0002_002                                                             COMPCODE4,
                                CR0002_003                                                             COMPNAME4,
                                CR0002_004                                                             equityRatio3,
                                ROW_NUMBER() over (partition by A.ITCODE order by TT1.CR0002_004 DESC) rowNums
                         from (
                                  select *
                                  from (
                                           select A.*,
                                                  CR0002_002                                                             COMPCODE3,
                                                  CR0002_003                                                             COMPNAME3,
                                                  CR0002_004                                                             equityRatio2,
                                                  ROW_NUMBER() over (partition by A.ITCODE order by TT1.CR0002_004 DESC) rowNum
                                           from (
                                                    SELECT ITCODE,/*公司代码,*/
                                                           ITNAME,/*公司名称,*/
                                                           CR0001_008,/*公司社会信用代码,*/
                                                           CR0002_002 COMPCODE2,/*大股东代码,*/
                                                           CR0002_003 COMPNAME2,/*大股东名称,*/
                                                           CR0002_004 equityRatio1/*持股比例,*/
                                                    from (
                                                             SELECT ROW_NUMBER() over (partition by T.ITCODE order by TT1.CR0002_004 DESC) rowNum,
                                                                    T.ITCODE                                                               ITCODE,
                                                                    T.ITNAME                                                               ITNAME,
                                                                    T.CR0001_008                                                           CR0001_008,
                                                                    ifnull(TT1.CR0002_002, 0)                                              CR0002_002,
                                                                    ifnull(TT1.CR0002_003, 0)                                              CR0002_003,
                                                                    ifnull(TT1.CR0002_004, 0)                                              CR0002_004
                                                             FROM fcdb.tcr0001 T
                                                                      left join fcdb.tq_fin_proindicdata tfp on tfp.COMPCODE = T.ITCODE
                                                                      left join fcdb.tcr0002_1 TT1 on TT1.ITCODE = T.ITCODE and TT1.CR0002_004 >= 10
                                                             where tfp.COMPCODE is not null /*and T.ITNAME like '%同济堂%'*/
                                                         ) tt
                                                    where rowNum = 1
                                                ) A
                                                    left join fcdb.tcr0002_1 TT1 on TT1.ITCODE = A.COMPCODE2 and TT1.CR0002_004 >= 10
                                       ) t
                                  where rowNum = 1
                              ) A
                                  left join fcdb.tcr0002_1 TT1 on TT1.ITCODE = A.COMPCODE3 and TT1.CR0002_004 >= 10
                     ) t
                where rowNums = 1''')  # 正式计算用CCX_BOND_yield +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    row0 = cursor.fetchall()
    row0 = np.array(row0)
    len0 = len(row0)
    codexydm = {}  # 信用代码
    codegsmc = {}  # 公司名称
    code = {}

    maxcode = {} # 最大值

    gzscore = {}
    i0 = 0
    period = 365
    for i in range(len0):
        arr = []
        if row0[i,0] != '0' and row0[i, 1] is not None:
            codexydm[row0[i,0]] = row0[i, 1]
            codegsmc[row0[i, 2]] = row0[i, 1]
            code[row0[i, 1]] = row0[i, 2]

            # 获取对象儿子  判断哪个儿子大
            cursor.execute('''
                   select distinct TT1.ITCODE, TT1.ITNAME, T.ITCODE ITCODE1, T.ITNAME ITNAME1
                    from fcdb.tcr0001 T
                             left join fcdb.tq_fin_proindicdata tfp on tfp.COMPCODE = T.ITCODE
                             left join fcdb.tcr0002_1 TT1 on TT1.CR0002_002 = T.ITCODE
                    where TT1.CR0002_004 >= 10
                      and TT1.ITCODE is not null
                      and tfp.COMPCODE is not null
                      and T.ITCODE = '%s' ''' % (row0[i, 1]))
            son = cursor.fetchall()
            son = np.array(son)
            sonLen = len(son)
            # 判断哪个儿子大
            son_max=0
            for son_i in range(sonLen):
                son_name=son[son_i,1]
                son_shareholder=son[son_i,3]
                for son_j in range(1, nrow):
                    if son_name == row[j, 2] and son_shareholder == row[j, 4]:
                        son_max=max(float(son_max),float(row[son_j, j0]))
                        print(son_name, son_shareholder,son_max)
            for k in range(1, 3):
                name = row0[i, 2 * k]
                shareholder = row0[i, 2 * (k + 1)]
            # print(name + "-------")
                for j in range(1, nrow):
                    # print(row[j, 2] + "----------------------------------------------------------------")
                    if name == row[j, 2] and shareholder == row[j, 4] :
                        # 查找股权质押并加入数组 1 * 0.9 * 0.8
                        if k==1:
                            arr.append(float(row[j, j0])*0.9)
                        elif k==2:
                            arr.append(float(row[j, j0])*0.8)
                        break

            a = np.array(arr)
            if len(a):
                maxData = a[np.argmax(a)]
            else:
                maxData = 0
                print(float(son_max),maxData)
            maxData=max(float(son_max),maxData)

            maxcode[row0[i, 1]]=maxData
            x =maxData
            # 修改后：
            if x < 30:
                gz = 0
            elif x >= 60:
                gz = x / 10 - 4
            else:
                gz = x / 15 - 2
            gzdf = gz / 6
            gzscore[row0[i, 1]] = [gz, gzdf]  # 公司得分
            print(row0[i, 2], maxData,gz,gzdf)
            i0 = i0 + 1


    # 复制
    row_copy=row[:]

    # gzscore = {}
    associate = {}
    # gzgroup = {}

    # print('j0=',j0)

    # wb = xlsxwriter.Workbook('C:\L_program_cal\股债验证（万得）(兼容财汇的方式).xlsx')
    # sheet = wb.add_worksheet('sheet0')


    # maxscore = {}
    # 查找excel中的相关字段 row
    # 2 ,4,6,8
    # 循环表
    # for i in range(len0):
    #     print(i)
    #     arr = []
    #     for k in range(1, 4):
    #         name = row0[i, 2 * k]
    #         shareholder = row0[i, 2 * (k + 1)]
    #         # print(name + "-------")
    #         for j in range(1, nrow):
    #             # print(row[j, 2] + "----------------------------------------------------------------")
    #             if name == row[j, 2] and shareholder == row[j, 4]:
    #                 # 查找股权质押并加入数组 1 * 0.9 * 0.8
    #                 arr.append(row[j, j0])
    #                 break
    #     # 获取最大值
    #     a = np.array(arr)
    #     if len(a):
    #         max = np.argmax(a)
    #         maxscore[row0[i, 0]] = max
        # else:
        #     max = None
        # # xudm:max
        # maxscore[row0[i,0]]=max





    # for i in range(1, nrow):
    #     if row[i, 3] in codexydm.keys() and float(row[i, 5]) >= 10:  # 股份比例小于10认为控制不了
    #         gzgroup[codexydm[row[i, 3]]] = row[i]
    #     else:
    #         if row[i, 2] in codegsmc.keys():
    #             gzgroup[codegsmc[row[i, 2]]] = row[i]
    #     if row[i, 4] in codegsmc.keys():
    #         gzgroup[codegsmc[row[i, 4]]] = row[i]

    # sheet.write(0, 0, '打分主体')
    # sheet.write(0, 1, '上市公司')
    # sheet.write(0, 2, '第一大股东')
    # sheet.write(0, 3, '股债参数')
    # sheet.write(0, 4, '计算取质押比例')
    # sheet.write(0, 5, '当前质押比例')
    # sheet.write(0, 6, 'period内平均质押比例')

    # i0 = 0
    # period = 365
    #
    # for key in sorted(maxcode.keys()):
    #     # keylen = len(code[key])
    #     # gzgroup[key] = np.array(gzgroup[key])
    #
    #     x = float(maxcode[key])
    #     # 此处设置股票质押计算逻辑
    #     # 修改前
    #     #		if x>=50:
    #     #			gz=(x-40)/10
    #     #		else:
    #     #			gz=x/50
    #     #		gzdf=gz/6
    #
    #     # 修改后：
    #     if x < 30:
    #         gz = 0
    #     elif x >= 60:
    #         gz = x / 10 - 4
    #     else:
    #         gz = x / 15 - 2
    #     gzdf = gz / 6
    #     gzscore[key] = [gz, gzdf]  # 公司得分
    #     i0 = i0 + 1

    # for key in sorted(gzgroup.keys()):
    #     print (time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))
    #     keylen = len(gzgroup[key])
    #     gzgroup[key] = np.array(gzgroup[key])
    #     # 改成查询快----------------------------------
    #     cursor.execute('''select
    #                     IFNULL(CR0001_008,0) CR0001_008,
    #                     ITCODE,
    #                    ITNAME,
    #                    COMPCODE2 ,
    #                    COMPNAME2 ,
    #                    COMPCODE3 ,
    #                    COMPNAME3 ,
    #                    COMPCODE4 ,
    #                    COMPNAME4
    #             from (
    #                      select A.*,
    #                             CR0002_002                                                             COMPCODE4,
    #                             CR0002_003                                                             COMPNAME4,
    #                             CR0002_004                                                             equityRatio3,
    #                             ROW_NUMBER() over (partition by A.ITCODE order by TT1.CR0002_004 DESC) rowNums
    #                      from (
    #                               select *
    #                               from (
    #                                        select A.*,
    #                                               CR0002_002                                                             COMPCODE3,
    #                                               CR0002_003                                                             COMPNAME3,
    #                                               CR0002_004                                                             equityRatio2,
    #                                               ROW_NUMBER() over (partition by A.ITCODE order by TT1.CR0002_004 DESC) rowNum
    #                                        from (
    #                                                 SELECT ITCODE,/*公司代码,*/
    #                                                        ITNAME,/*公司名称,*/
    #                                                        CR0001_008,/*公司社会信用代码,*/
    #                                                        CR0002_002 COMPCODE2,/*大股东代码,*/
    #                                                        CR0002_003 COMPNAME2,/*大股东名称,*/
    #                                                        CR0002_004 equityRatio1/*持股比例,*/
    #                                                 from (
    #                                                          SELECT ROW_NUMBER() over (partition by T.ITCODE order by TT1.CR0002_004 DESC) rowNum,
    #                                                                 T.ITCODE                                                               ITCODE,
    #                                                                 T.ITNAME                                                               ITNAME,
    #                                                                 T.CR0001_008                                                           CR0001_008,
    #                                                                 ifnull(TT1.CR0002_002, 0)                                              CR0002_002,
    #                                                                 ifnull(TT1.CR0002_003, 0)                                              CR0002_003,
    #                                                                 ifnull(TT1.CR0002_004, 0)                                              CR0002_004
    #                                                          FROM fcdb.tcr0001 T
    #                                                                   left join fcdb.tq_fin_proindicdata tfp on tfp.COMPCODE = T.ITCODE
    #                                                                   left join fcdb.tcr0002_1 TT1 on TT1.ITCODE = T.ITCODE and TT1.CR0002_004 >= 10
    #                                                          where tfp.COMPCODE is not null and T.ITCODE = '%s'
    #                                                      ) tt
    #                                                 where rowNum = 1
    #                                             ) A
    #                                                 left join fcdb.tcr0002_1 TT1 on TT1.ITCODE = A.COMPCODE2 and TT1.CR0002_004 >= 10
    #                                    ) t
    #                               where rowNum = 1
    #                           ) A
    #                               left join fcdb.tcr0002_1 TT1 on TT1.ITCODE = A.COMPCODE3 and TT1.CR0002_004 >= 10
    #                  ) t
    #             where rowNums = 1''' % (key))  # 正式计算用CCX_BOND_yield +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #     rowindex = cursor.fetchone()
    #     print(rowindex)
    #     arr = []
    #     max = 0
    #     if rowindex is not None:
    #         rowindex = np.array(rowindex)
    #         for k in range(1, 4):
    #             name = rowindex[2 * k]
    #             shareholder = rowindex[2 * (k + 1)]
    #             # print(name + "-------")
    #             for j in range(1, nrow):
    #                 # print(row[j, 2] + "----------------------------------------------------------------")
    #                 if name == row_copy[j, 2] and shareholder == row_copy[j, 4]:
    #                     # 查找股权质押并加入数组 1 * 0.9 * 0.8
    #                     arr.append(row_copy[j, j0])
    #                     break
    #         # 获取最大值
    #         a = np.array(arr)
    #         if len(a):
    #             max = a[np.argmax(a)]
    #     else:
    #         max=float(gzgroup[key][j0])
    #     print(max)
    #
    #     # x = float(gzgroup[key][j0])
    #     x = max
    #     # x = float(maxscore[gzgroup[key][3]])
    #     # 此处设置股票质押计算逻辑
    #     # 修改前
    #     #		if x>=50:
    #     #			gz=(x-40)/10
    #     #		else:
    #     #			gz=x/50
    #     #		gzdf=gz/6
    #
    #     # 修改后：
    #     if x < 30:
    #         gz = 0
    #     elif x >= 60:
    #         gz = x / 10 - 4
    #     else:
    #         gz = x / 15 - 2
    #     gzdf = gz / 6
    #     gzscore[key] = [gz, gzdf]  # 公司得分
    #     i0 = i0 + 1
    # 此处需要50s
    cursor.execute('''
       SELECT ITCODE     公司代码,
       ITNAME     公司名称,
       CR0001_008 公司社会信用代码,
       CR0002_002 大股东代码,
       CR0002_003 大股东名称,
       CR0002_004 持股比例,
       ratio      累计质押比例
       from (
         SELECT ROW_NUMBER() over (partition by T.ITCODE order by TT1.CR0002_004 DESC) rowNum,
                T.ITCODE                                                               ITCODE,
                T.ITNAME                                                               ITNAME,
                T.CR0001_008                                                           CR0001_008,
                ifnull(TT1.CR0002_002, 0)                                              CR0002_002,
                ifnull(TT1.CR0002_003, 0)                                              CR0002_003,
                ifnull(TT1.CR0002_004, 0)                                              CR0002_004,
                ifnull(AA.SISHAERSCUMRTO / TT1.CR0002_004, 0)                          ratio
         FROM fcdb.tcr0001 T
             left join fcdb.tq_fin_proindicdata tfp on tfp.COMPCODE = T.ITCODE
                  left join fcdb.tcr0002_1 TT1 on TT1.ITCODE = T.ITCODE and TT1.CR0002_004 >= 10
                  left join (select COMPCODE, SISHAERSCUMRTO, DECLAREDATE
                             from (
                                      select A.COMPCODE,
                                             AA.SISHAERSCUMRTO,
                                             AA.DECLAREDATE,
                                             row_number()
                                                     over (partition by A.COMPCODE order by AA.DECLAREDATE DESC) idx
                                      from TQ_COMP_FREEZINGSK A
                                               left join fcdb.TQ_COMP_SFRZDATE AA on A.SFRZID = AA.SFRZID
                                      where AA.DECLAREDATE < %s
                                  ) t
                             where idx = 1) AA on AA.COMPCODE = T.ITCODE
       where tfp.COMPCODE is not null
        ) tt
       where rowNum = 1 order by ITCODE''' % (datenow))

    row = cursor.fetchall()
    row = np.array(row)
    length = len(row)
    associate = {}
    for i in range(length):
        if row[i, 3] != '0' and '国有资产' not in row[i, 4] and '香港中央结算' not in row[i, 4] and '人民政府' not in row[
            i, 4] and '管理委员会' not in row[i, 4]:  # 找关联公司集合
            if row[i, 0] in associate.keys():
                associate[row[i, 0]][row[i, 3]] = 0
            else:
                associate[row[i, 0]] = {}
                associate[row[i, 0]][row[i, 3]] = 0

            if row[i, 3] in associate.keys():
                associate[row[i, 3]][row[i, 0]] = 0
            else:
                associate[row[i, 3]] = {}
                associate[row[i, 3]][row[i, 0]] = 0

            for key in associate[row[i, 0]].keys():
                if key not in associate[row[i, 3]].keys():
                    associate[row[i, 3]][key] = 0

            for key in associate[row[i, 3]].keys():
                if key not in associate[row[i, 0]].keys():
                    associate[row[i, 0]][key] = 0

    calculated = {}
    for key in sorted(associate.keys(), reverse=True):
        if key not in calculated.keys():
            former = {}
            later = {}
            x = 0
            for key1 in associate[key].keys():
                former[key1] = 0

            while x == 0:
                for key2 in list(former.keys()):
                    for key22 in associate[key2].keys():
                        later[key22] = 0
                if len(former.keys()) == len(later.keys()):
                    x = 1
                else:
                    former = later
                    x = 0
            for key3 in later.keys():
                for key33 in later.keys():
                    associate[key3][key33] = 0
            for key4 in later.keys():
                calculated[key4] = 0

    yy = len(gzscore.keys())
    y = len(associate.keys())

    return gzscore, associate


guzhai('20200512');

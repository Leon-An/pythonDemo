import pandas as pd
import openpyxl

# 地区信息表
df_location = pd.read_excel("F:\\Document\\code\\demo\\20200430累计城投分类明细.xlsx" )
df_location.head()
df_location = df_location[[ "发行人"]]
df_location.head()


# 数据库导出表
df_number = pd.read_excel("F:\\Document\\code\\demo\\债券发行.xlsx")
df_number.head()

# 只筛选第二个表的少量的列（只选取表二中市区和用户人数）
# 发行起始日	代码	证券简称	发行额(亿)	期限(年)	到期日	发行债券评级	主体评级	担保人	特殊条款	发行利率	发行人	发行人企业性质	发行人地域	发行人Wind行业(一级)	发行人Wind行业(二级)	发行人证监会行业	Wind债券类型(一级)	Wind债券类型(二级)	中债债券类型(一级)	中债债券类型(二级)	主承销商	承销金额主承分摊	副主承	分销商	发行截止日
# df_number = df_number[[ "发行人", "代码","证券简称"]]
# df_number.head()

df_merge = pd.merge(left=df_location, right=df_number, left_on="发行人", right_on="发行人")
df_merge.head()

df_merge.to_excel("F:\\Document\\code\demo\\合并后的数据表.xlsx", index=False)

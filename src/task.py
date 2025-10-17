from abc import abstractmethod
from data_prompt_templates import PromptTemplate
import csv
from io import StringIO
from data import global_delimiter, get_label_map, read_csv, get_ignore_title
import pandas as pd
import wandb
import datetime
import os
from tqdm import tqdm


def match(test_df, predict_df, columns_to_compare):
    # 初始化存储TP, FP, FN的DataFrame
    tp_data = []
    fp_data = []
    fn_data = []

    grouped = test_df.groupby([test_df.columns[4], test_df.columns[6],  test_df.columns[11], test_df.columns[-1]]) #column 4,11 is alias flag
    for group_name, test_group in grouped:
        predict_subset = predict_df[(predict_df.iloc[:, -1] == group_name[-1])&(predict_df.iloc[:, 6]== group_name[1])]
        match_found = False
        first_row = ''
        for index, row in test_group.iterrows():
            first_row = row
            if predict_subset.empty:
                break
            for predict_group_name, predict_group in predict_subset.groupby(columns_to_compare[:-1]):
                if all(row.iloc[col] == predict_group_name[idx] for idx,col in enumerate(columns_to_compare[:-1])):
                    match_found = True
                    tp_data.append(row)
                    break
            if match_found:
                break
        if not match_found:
            if first_row[5] == 'H' or first_row[12] == 'H':
                continue
            fn_data.append(first_row)

    grouped = predict_df.groupby([predict_df.columns[4],test_df.columns[6], predict_df.columns[11], predict_df.columns[-1]])
    for group_name, group in grouped:
        test_subset = test_df[(test_df.iloc[:, -1] == group_name[-1])&(test_df.iloc[:, 6] == group_name[1])]
        first_row = ''
        match_found = False
        for index, row in group.iterrows():
            first_row = row
            if test_subset.empty:
                break
            for test_group_name, test_group in test_subset.groupby(columns_to_compare[:-1]):
                if all(row.iloc[col] == test_group_name[idx] for idx,col in enumerate(columns_to_compare[:-1])):
                    match_found = True
                    break
            if match_found:
                break
        if not match_found:
            if first_row[5] == 'H' or first_row[12] == 'H':
                continue
            fp_data.append(first_row)

    # 将列表转换为DataFrame
    tp = pd.DataFrame(tp_data)
    fp = pd.DataFrame(fp_data)
    fn = pd.DataFrame(fn_data)
    return tp, fp, fn


def query(chain, queries):
    """
    feed batch to LLM. seems to better performance by one record.
    """
    return chain.batch(queries, {"max_concurrency": 16})


def calculate_metrics(group, predict_group, columns_to_compare):
    tp, fp, fn = match(group, predict_group, columns_to_compare)
    tp_n = len(tp)
    fp_n = len(fp)
    fn_n = len(fn)
    p = tp_n / (tp_n + fp_n) if tp_n + fp_n > 0 else 0
    r = tp_n / (tp_n + fn_n) if (tp_n + fn_n) > 0 else 0
    f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0
    return tp_n, fp_n, fn_n, p, r, f1, tp, fp, fn


def calculate_metrics_by_group(columns, table_name, test_df, predict_df, columns_to_compare, wandb_open):
    group_column_list = []
    if len(columns) > 1:
        for column_num in columns:
            group_column_list.append(test_df.columns[column_num])
    else:
        group_column_list = test_df.columns[columns[0]]
    grouped = test_df.groupby(group_column_list)
    d_table = wandb.Table(columns=["type", "TP", "FP", "FN", "Precision", "Recall", "F1 Score"])
    for group_name, group in tqdm(grouped,desc="Processing Group metrics", leave=True):
        condition = None
        # 初始化条件表达式
        if len(columns) == 1:
            group_name = [group_name]
        for column, column_name in zip(columns, group_name):
            column_condition = predict_df.iloc[:, column] == column_name
            # 如果是第一个条件，直接赋值给condition
            if condition is None:
                condition = column_condition
            else:
                condition = condition & column_condition
        predict_group = predict_df[condition]
        tp_n, fp_n, fn_n, p, r, f1, tp, fp, fn = calculate_metrics(group, predict_group, columns_to_compare)
        d_table.add_data(str(group_name), tp_n, fp_n, fn_n, p, r, f1)
    print(d_table.get_dataframe().to_string(index=False))
    if wandb_open:
        wandb.log({table_name: d_table})


class Task:
    def __init__(self, model, data_handler, **kwargs):
        self.task = kwargs['task']
        self.model = model
        self.data_handler = data_handler
        self.templates = PromptTemplate(data_handler.datasource)

    def save(self, output, data, *args):
        """
        save result
        """
        csv_data = [item.split('\n\n')[1] if '\n\n' in item else item for item in data]
        csv_file = StringIO('\n'.join(csv_data))
        csv_reader = csv.reader(csv_file, delimiter=global_delimiter)
        return csv_reader

    def evaluate(self, test_data_path, predict_data_path, doc_dict, **kwargs):
        wandb_open = kwargs['wandb_open']
        columns_to_compare = kwargs['columns_to_compare']
        columns_to_group = kwargs['columns_to_group']
        # 读取CSV文件
        test_df = read_csv(test_data_path)
        if os.path.exists(predict_data_path):
            predict_df = read_csv(predict_data_path)
        else:
            empty_list = [['_', 'country', '_', '0', '[0, 0]', '0', '0', '0', '[0, 0]', '0', '0', '_']]
            predict_df = pd.DataFrame(empty_list)
        # get predict lable list.
        label_map = get_label_map()
        ignore_titles = get_ignore_title()
        # 获取最后一列的列名
        last_column = predict_df.columns[-1]
        # 使用isin()方法来检查最后一列的值是否在ignore_titles中，然后取反（~）来选择不在ignore_titles中的行
        predict_df = predict_df[~predict_df[last_column].isin(ignore_titles)]
        # 获取最后一列的列名
        last_column = test_df.columns[-1]
        # 使用isin()方法来检查最后一列的值是否在ignore_titles中，然后取反（~）来选择不在ignore_titles中的行
        test_df = test_df[~test_df[last_column].isin(ignore_titles)]

        predict_df[1] = predict_df[1].map(lambda x: label_map.get(x, x))
        predict_df[8] = predict_df[8].map(lambda x: label_map.get(x, x))
        predict_df[6] = predict_df[6].map(lambda x: label_map.get(x, x))
        test_df[1] = test_df[1].map(lambda x: label_map.get(x, x))
        test_df[8] = test_df[8].map(lambda x: label_map.get(x, x))
        predict_label_list = predict_df.iloc[:, 1].unique()
        test_df = test_df[test_df[1].isin(predict_label_list)]
        print("start calculate micro metrics...")
        tp_n, fp_n, fn_n, p, r, f1, tp, fp, fn = calculate_metrics(test_df, predict_df, columns_to_compare)
        # print(f"{predict_data_path},F1={f1},Precision={p},Recall={r}")
        # print TP, FP and FN
        self.print_result(tp, fp, fn, doc_dict)
        all_table = wandb.Table(columns=["TP", "FP", "FN", "Precision", "Recall", "F1 Score"])
        all_table.add_data(tp_n, fp_n, fn_n, p, r, f1)
        print(all_table.get_dataframe().to_string(index=False))
        if wandb_open:
            wandb.log({f"{self.task} all_metrics": all_table})
        print("start calculate group metrics...")
        for column in columns_to_group:
            calculate_metrics_by_group(column[0], f"{self.task} {column[1]}_metrics", test_df, predict_df,
                                       columns_to_compare,
                                       wandb_open)

    def print_result(self, tp, fp, fn, doc_dict):
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        if not fn.empty:
            fn['article'] = fn.iloc[:, -1].astype(str).map(doc_dict)
            fn.to_csv(f'../data/result/{self.task}_FN_{timestamp}.csv', index=False)
        if not fp.empty:
            fp['article'] = fp.iloc[:, -1].astype(str).map(doc_dict)
            fp.to_csv(f'../data/result/{self.task}_FP_{timestamp}.csv', index=False)
            tp.to_csv(f'../data/result/{self.task}_TP_{timestamp}.csv', index=False)

    @abstractmethod
    def process(self, **kwargs):
        pass

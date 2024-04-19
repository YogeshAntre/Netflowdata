from utilities.crud import*
import pandas as pd
import json
def outgoing_func_app(gte,lte,device,interface):
        #print('******** out app*********')
        graph_list_values_src=[]
        graph_list_values_dst=[]

        graph_query={"size":0,"query":{"bool":{"must":[{"range":{"time_stamp":{"gte":gte,"lte":lte}}},{"match":{"devname.keyword":device}}]}},"aggs":{"outgoing_dir_src_filters":{"filter":{"bool":{"must":[{"match":{"srcintfrole.keyword":"wan"}},{"match":{"srcintf.keyword":interface}}]}},"aggs":{"outgoing_dir_src_ip":{"terms":{"field":"app.keyword","size":10000},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {"min": gte,"max":  lte}},"aggs":{"sent_byte_sum":{"sum":{"field":"sent_byte"}}}}}}}},"dst_filters":{"filter":{"bool":{"must":[{"match":{"dstintfrole.keyword":"wan"}},{"match":{"dstintf.keyword":interface}}]}},"aggs":{"outgoing_dir_dst_ip":{"terms":{"field":"app.keyword","size":10000},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {"min": gte,"max":  lte}},"aggs":{"rcvd_byte_sum":{"sum":{"field":"rcvd_byte"}}}}}}}}}}
        #return graph_query
        graph_resp = get_by_query_agg(index_name = "abg_processed_update", query = graph_query)
        #print('graph_resp',graph_resp)
        #return graph_resp
            
        if not graph_resp:
                    return []

        graph_respons_dst = [res for res in graph_resp["aggregations"]["outgoing_dir_src_filters"]["outgoing_dir_src_ip"]["buckets"]]
        #print("graph_respons_dst",graph_respons_dst)
        graph_respons_src = [res for res in graph_resp["aggregations"]["dst_filters"]["outgoing_dir_dst_ip"]["buckets"]]
        #print("graph_respons_src",graph_respons_src)
        #print(graph_respons)
        for graph in graph_respons_src:
                graph_data_src_values = []
                for date in graph.get('5_min_sum_buckets').get('buckets'):
                    graph_data_src = []

                    graph_data_src.append(date["key_as_string"][:-8] )
                    graph_data_src.append(round((date["rcvd_byte_sum"]["value"]*8/300),2))
                    graph_data_src_values.append(graph_data_src)
                graph_dict = {
                                "appname": graph.get("key"),
                                "data": graph_data_src_values
                            }            
                graph_list_values_src.append(graph_dict)
        for graph in graph_respons_dst:
                graph_data_values_dst = []
                for date in graph.get('5_min_sum_buckets').get('buckets'):
                    graph_data_dst = []

                    graph_data_dst.append(date["key_as_string"][:-8] )
                    graph_data_dst.append(round((date["sent_byte_sum"]["value"]*8/300),2))
                    graph_data_values_dst.append(graph_data_dst)
                graph_dict = {
                                "appname": graph.get("key"),
                                "data": graph_data_values_dst
                            }            
                graph_list_values_dst.append(graph_dict)
        #print(graph_list_values_dst)
        #print("***************************")
        #print(graph_list_values_src)
        from collections import defaultdict

        def merge_lists(graph_list_values_dst, graph_list_values_src):
            merged_data = defaultdict(list)
            for item in graph_list_values_dst + graph_list_values_src:
                appname = item['appname']
                data = item['data']
                for timestamp, value in data:
                    found = False
                    for existing_data in merged_data[appname]:
                        if existing_data[0] == timestamp:
                            existing_data[1] += value
                            found = True
                            break
                    if not found:
                        merged_data[appname].append([timestamp, value])
            result = [{'appname': appname, 'data': data} for appname, data in merged_data.items()]
            
            #print('Merged Data', result)
            return result
        final_graph_list_values=merge_lists(graph_list_values_dst, graph_list_values_src)
        #return graph_list_values_src
        result = {}
        for item in final_graph_list_values:
            appname = item.get("appname")
            values = [x[1] for x in item["data"]]
            total = round(sum(values),2)
            minimum = round(min(values),2)
            maximum = round(max(values),2)
            average = round(total / len(values),2)
            result[appname] = {

                "sum": round(total,2),
                "min": round(minimum,2),
                "max": round(maximum,2),
                "avg": round(average,2),
            }
        sorted_metrics = sorted(result.items(), key=lambda x: x[1]["avg"], reverse=True)
        top_10_apps_list = []
        for metric_name, metric_data in sorted_metrics:
            if len(top_10_apps_list) <10:
                data = {
                    'appname': metric_name ,
                    'sum' : round(metric_data["sum"],2),
                    'min' : round(metric_data["min"],2),
                    'max' : round(metric_data["max"],2) ,
                    'avg' : round(metric_data["avg"],2) ,
                }
                top_10_apps_list.append(data)
        top_10_apps_name =[ ]
        for app_name in top_10_apps_list:
            top_10_apps_name.append(app_name.get("appname"))
        top_10_graph_list = []
        others_graph_list = []
        for graph in final_graph_list_values: 
            if  graph.get("appname") not in top_10_apps_name : 
                others_graph_list.append(graph)     
            else:
               
                top_10_graph_list.append(graph)
        data_dict = {app.get("appname"): app for app in top_10_graph_list}

        top_10_graph_list1 = [data_dict[app_name] for app_name in top_10_apps_name]
        
        time_interval_totals = {}
        for app_entry in others_graph_list:
            for timestamp, byte_count in app_entry['data']:
                if timestamp in time_interval_totals:
                    time_interval_totals[timestamp] += byte_count
                else:
                    time_interval_totals[timestamp] = byte_count

        others_list = []
        time_ = []
        for k,v in time_interval_totals.items():
            others = []
            others.append(k)
            others.append(round(v,2))
            time_.append(v)
            others_list.append(others)
        if time_ :
            total_sum = round(sum(time_),2)
            min_value = round(min(time_),2)
            max_value = round(max(time_),2)
            average = round(sum(time_) / len(time_),2)
            output = {
                "appname": "Others",
                "sum": round(total_sum,2),
                "min": round(min_value,2),
                "max": round(max_value,2),
                "avg": round(average,2),
            }
            top_10_apps_list.append(output)
        if others_list :
            graph_dict1 = {
                    'appname': "others" ,
                    "data": others_list
                }
            top_10_graph_list1.append(graph_dict1)
        # data=dict(list_values = top_10_apps_list, graph_list_values  = top_10_graph_list1)
        # df = pd.DataFrame(data)
        # df.to_excel('top_app_outgoing.xlsx', index=False)
        
        return dict(list_values = top_10_apps_list, graph_list_values  = top_10_graph_list1)


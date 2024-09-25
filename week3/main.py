from openai import OpenAI
import json
import time

client = OpenAI(
    api_key="sk-T6SlqfUnyFytejvA3c1584F87d6343878232185e26243b1d",
    base_url="https://api.apiyi.com/v1",
)

def modify_config(service_name,key,value):
    print("\n函数调用的参数: ", service_name,key,value)
    return json.dumps({"gateway": "vendor 已修改为 alipay"})

def restart_service(service_name):
    print("\n函数调用的参数: ", service_name)
    return json.dumps({"restart": "已重启gateway服务"})

def apply_manifest(resource_type,image):
    print("\n函数调用的参数: ", resource_type,image)
    return json.dumps({"deployment": "apply nginx pod"})


def run_conversation():
    # 步骤一：把所有预定义的 function 传给 chatgpt
    query = input("输入查询指令：")
    messages = [
        {
            "role": "system",
            "content": "你是kubernetes管理员，请根据指令修改配置以及相关处理，并返回对应数据。",
        },
        {
            "role": "user",
            "content": query,
        },
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "modify_config",
                "description": "修改 gateway 的配置",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": 'gateway配置变更，例如：{service="gateway", key="vendor", value="alipay"}',
                        },
                        "value": {
                            "type": "string",
                            "description": 'gateway配置变更，例如：{value="alipay"}"',
                        },
                        "key": {
                            "type": "string",
                            "description": 'gateway配置变更，例如：{key="vendor"}',
                        },
                    },
                    "required": ["gateway", "vendor", "alipay"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "restart_service",
                "description": "重启 gateway 服务",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": '重启 gateway 服务，例如：{service="gateway"}',
                        },
                    },
                    "required": ["service_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "apply_manifest",
                "description": "deployment部署nginx",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": 'deployment部署nginx，例如：{resource_type="deployment", image="nginx:latest"}',
                        },
                        "image": {
                            "type": "string",
                            "description": 'deployment部署nginx，例如：{image="nginx:latest"}',
                        },
                    },
                    "required": ["resource_type","image"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    print("\nChatGPT want to call function: ", tool_calls)
    # 步骤二：检查 LLM 是否调用了 function
    if tool_calls is None:
        print("not tool_calls")
    if tool_calls:
        available_functions = {
            "modify_config": modify_config,
            "restart_service": restart_service,
            "apply_manifest": apply_manifest,
        }
        messages.append(response_message)
        # 步骤三：把每次 function 调用和返回的信息传给 model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        # 步骤四：把 function calling 的结果传给 model，进行对话
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return response.choices[0].message.content


for i in range(10):
    print("LLM Res: ", run_conversation())

# print("LLM Res: ", run_conversation())

#!/usr/bin/env python3
"""
External Communication XML Example - ExternalIO Mode

This example shows how to use CommExternalInput and CommExternalOutput nodes in XML configuration
to communicate with external systems through the behavior forest using the new ExternalIO pattern.
"""

import asyncio
from abtree import BehaviorForest, load_from_xml_string, Action, Status, register_node
from openai import OpenAI


class LLMModel(Action):
    
    def __init__(self, name: str = ""):
        super().__init__(name)

    async def execute(self, api_key: str = None, api_base: str = None, model: str = None):
        print(f"🔍 LLMModel.execute 被调用，参数: api_key={api_key[:10] if api_key else 'None'}..., api_base={api_base}, model={model}")
        
        try:
            client = OpenAI(api_key=api_key, api_base=api_base)
            self.set_port("model", client)
            print(f"✅ OpenAI客户端创建成功")
            return Status.SUCCESS
        except Exception as e:
            print(f"❌ LLMModel执行错误: {e}")
            return Status.FAILURE


class LLMChat(Action):
    
    async def execute(self, model: any = None, messages: str = None, response: any = None, stream: bool = True):
        print(f"🔍 LLMChat.execute 被调用，参数: model={type(model)}, messages={messages}")
        
        try:
            # 确保messages是列表格式
            if isinstance(messages, str):
                messages_list = [{"role": "user", "content": messages}]
            else:
                messages_list = messages
                
            response = model.chat.completions.create(
                model="gpt-3.5-turbo",  # 使用具体的模型名称
                messages=messages_list,
                stream=False  # 改为False以便调试
            )
            
            # 设置输出端口
            self.set_port("response", response.choices[0].message.content)
            print(f"✅ LLM响应: {response.choices[0].message.content}")
            
            return Status.SUCCESS
        except Exception as e:
            print(f"❌ LLMChat执行错误: {e}")
            return Status.FAILURE

async def external_output_handler(output_info):
    print(f"🔗 External output sent: {output_info}")

async def main():
    # XML configuration for external communication using ExternalIO pattern
    xml_config = """
    <BehaviorForest name="LLMForest">
        <BehaviorTree name="LLMTree">
            <CommExternalInput name="chat_input" channel="chat_input" timeout="3.0" data="{messages}"/>
            <Log message="{messages}" />
            <LLMModel api_key="your-api-key" api_base="https://api.openai.com/v1" model="gpt-3.5-turbo" />
            <LLMChat model="{model}" messages="{messages}" />
            <CommExternalOutput name="chat_output" channel="chat_output" data="{response}"/>
        </BehaviorTree>
    </BehaviorForest>
    """
    

    register_node("LLMModel", LLMModel)
    register_node("LLMChat", LLMChat)
    forest = load_from_xml_string(xml_config)    
    forest.on_output("chat_output", external_output_handler)
    
    await forest.start()

    # 修复输入数据格式
    await forest.input("chat_input", {"messages": "你好，我是小明，很高兴认识你"})

    await asyncio.sleep(1)

    output_data = await forest.output("chat_output")
    print(f"🔗 External output data received: {output_data}")
    
    await forest.stop()

if __name__ == "__main__":
    asyncio.run(main()) 
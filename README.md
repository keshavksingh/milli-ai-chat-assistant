# milli-ai-chat-assistant

 [Browser Client] --(WebSocket)--> [FastAPI WebSocket Server (gateway_server)] --(gRPC)--> [SupportService Controller] (gRPC)
                                                                                           |
                                                                                           |---> [KnowledgeService] (gRPC)
                                                                                           |---> [LLMService] (gRPC)


![image](https://github.com/user-attachments/assets/a71fa951-83bc-412e-938b-04c9e1538b83)


![image](https://github.com/user-attachments/assets/23ccdd78-fa2b-489b-b768-ebed77dd40f9)

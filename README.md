# Asar 聊天機器人設計平台

<img src="img/asar_logo.png" style="width: 30%;">

## 簡介
Asar是一款輕量級聊天機器人設計平台，將聊天機器人與樹莓派結合，提供一條龍的聊天機器人服務部署流程。開發者僅需一片微型單板電腦，就能輕鬆創造專屬於自己的聊天機器人。

以往，開發者需要掌握多種程式語言及專業技術，才有能力建立聊天機器人服務。而Asar平台的出現大幅降低了此門檻。

Asar的系統架構採用容器化設計，實現快速建構和部署。在自然語言處理方面，Asar使用Transformer、ALBERT等近代深度學習技術，使聊天機器人具備自然語言理解能力。在開發者體驗方面，Asar提供專屬的視覺化設計工具，讓開發者以流程圖的思維來設計聊天劇本；以拖拉方塊的方式來編寫程式，進而控制樹莓派的周邊設備。此外，Asar提供了各大通訊平台的接口，簡化將聊天機器人整合至聊天室的步驟。在隱私方面，Asar平台完全運行於樹莓派上，無須依賴外部服務，降低個人資料外流的風險。受益於樹莓派的自由度、擴充性等優勢，Asar能夠應用於各種場景。


想了解更詳細的介紹，請參閱[報告書](doc/asar實務專題成果報告書(研究型).pdf)及[操作手冊](doc/操作手冊.pdf)

## 部署指南

1. 準備Raspberry Pi
    - 支援型號：4B、400
    - 記憶體需求：4GB以上
    - 作業系統：Raspberry Pi OS (64-bit)

2. 安裝Docker及Docker-Compose
    - [Docker Install documentation](https://docs.docker.com/install/)
    - [Docker-Compose Install documentation](https://docs.docker.com/compose/install/)

3. 創建docker-compose.yml

    ```yml
    version: "3.8"

    networks: # 創建Asar專用的Docker Network
    default:
        name: asar-prod

    volumes:
    rasa:    # 存放聊天機器人服務的資料
    actions: # 存放動作代理服務的資料
    data:    # 存放後端API服務的資料

    services:
    rasa: # 聊天機器人服務
        image: devilhyt/rasa:custom
        volumes:
        - rasa:/app
        - data:/data
        ports:
        - 5005:5005

    action: # 動作代理服務
        image: devilhyt/rasa-sdk:custom
        volumes:
        - actions:/app/actions
        ports:
        - 5055:5055
        privileged: true

    api: # 後端API服務
        image: devilhyt/asar-api:latest
        volumes:
        - actions:/actions
        - data:/data
        environment:
        SECRET_KEY: # Flask密鑰
        # 密鑰可用此指令生成
        # python -c 'import secrets; print(secrets.token_hex())'
        ASAR_USERNAME: admin # 管理員帳號
        ASAR_PASSWORD: admin # 管理員密碼
        RASA_API_HOST: rasa # 聊天機器人服務的別名
        ASAR_API_HOST: api # 後端API服務的別名
        ports:
        - 5500:5500

    web: # 前端網頁服務
        image: devilhyt/asar-web:latest
        environment:
        RASA_API_HOST: rasa # 聊天機器人服務的別名
        ASAR_API_HOST: api # 後端API服務的別名
        ports:
        - 80:80
        depends_on:
        - api
    ```

4. 啟動服務

    ```bash
    docker-compose up -d

    # If using docker-compose-plugin
    docker compose up -d
    ```

5. 登入Asar平台

    - http://127.0.0.1
    - http://localhost
    - http://raspberrypi

6. 開始設計聊天機器人

## Docker 環境變數

### 後端API服務

- 必要設定
    - SECRET_KEY：              API安全金鑰，用於session cookie的安全簽名
    - ASAR_USERNAME：           管理者帳號名
    - ASAR_PASSWORD：           管理者密碼
    - RASA_API_HOST：           聊天機器人服務的別名
    - ASAR_API_HOST：           後端API服務的別名
- 進階設定  
    - RASA_API_PROTOCOL：       聊天機器人服務的通訊協定，可選http或https
    - RASA_API_PORT：           聊天機器人服務的通訊埠
    - ASAR_API_PROTOCOL：       後端API服務的通訊協定，可選http或https
    - ASAR_API_PORT：           後端API服務的通訊埠
    - RASA_API_AGENT_PROTOCOL： 聊天機器人服務代理的通訊協定，可選http或https
    - RASA_API_AGENT_HOST：     聊天機器人服務代理的IP位址
    - RASA_API_AGENT_PORT：     聊天機器人服務代理的通訊埠
    - ASAR_API_AGENT_PROTOCOL： 後端API服務代理的通訊協定，可選http或https
    - ASAR_API_AGENT_HOST：     後端API服務代理的別名
    - ASAR_API_AGENT_PORT：     後端API服務代理的通訊埠
    - RASA_ACTIONS_ROOT：       動作代理服務的根目錄

### 前端網頁服務

- 必要設定
    - RASA_API_HOST：           聊天機器人服務的別名
    - ASAR_API_HOST：           後端API服務的別名
- 進階設定
    - RASA_API_PROTOCOL：       聊天機器人服務的通訊協定，可選http或https
    - RASA_API_PORT：           聊天機器人服務的通訊埠
    - ASAR_API_PROTOCOL：       後端API服務的通訊協定，可選http或https
    - ASAR_API_PORT：           後端API服務的通訊埠

## 文件結構

```
    .
    ├── rasa                            # 聊天機器人服務
    │   ├── build                       # 依賴檔案
    │   │   └── initial_project_zh      # rasa設定檔與自定義工具
    │   │       ├── custom_components   # NLP組件
    │   │       ├── custom_connectors   # 聊天平台接口
    │   │       └── ...
    │   └── Dockerfile
    ├── rasa-sdk                        # 動作代理服務
    │   ├── app                         # 初始專案
    │   │   └── actions
    │   ├── rasa-sdk                    # 主程式 (submodule)
    │   ├── requirements.txt            # Python依賴套件
    │   └── Dockerfile
    ├── api                             # 後端API服務
    │   ├── app                         # 主程式 (submodule)
    │   └── Dockerfile
    ├── web                             # 前端網頁服務
    │   ├── app                         # 主程式 (submodule)
    │   ├── templates                   # Nginx設定檔模板
    │   └── Dockerfile
    ├── docker-compose-dev.yml          # 用於開發環境的compose
    ├── docker-compose-prod.yml         # 用於生產環境的compose
    ├── doc                             # 說明文件
    ├── demo                            # 範例專案
    └── ...
```

# 協作者
- HsiangYi Tsai, [devilhyt](https://github.com/devilhyt) on Github
- Paxton, [Paxton90](https://github.com/Paxton90) on Github

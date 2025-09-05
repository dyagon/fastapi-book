// 聊天室JavaScript功能
const { createApp, ref, onMounted, onUnmounted, nextTick } = Vue;

function createChatApp() {
  return createApp({
    setup() {
      const title = ref("FastAPI Websocket 简易聊天室案例");
      const wsurl = ref("ws://127.0.0.1:8000/api/v1/room/socketws");
      const socket = ref(null);
      const messages = ref([]);
      const users = ref([]);
      const sendmsg = ref("");
      const messagesContainer = ref(null);
      const currentUser = ref("");

      // 从URL参数获取当前用户名
      const getCurrentUser = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const username = urlParams.get('username');
        if (username) {
          currentUser.value = username;
        } else {
          // 如果没有用户名参数，使用默认值或从其他地方获取
          currentUser.value = "用户" + Math.floor(Math.random() * 1000);
        }
      };

      const initSocket = () => {
        if (typeof WebSocket === "undefined") {
          alert("您的浏览器不支持socket");
          return;
        }

        // 实例化socket并链接到服务端的WebSocket
        const fullWsUrl = wsurl.value + window.location.search;
        socket.value = new WebSocket(fullWsUrl);

        // 监听socket连接
        socket.value.onopen = open;
        // 监听socket错误信息
        socket.value.onerror = error;
        // 监听socket消息
        socket.value.onmessage = getMessage;
        // 监听socket关闭
        socket.value.onclose = close;
      };

      const open = () => {
        console.log("socket连接成功");
        addSystemMessage("连接成功", "已连接到聊天室");
      };

      const error = () => {
        console.log("连接错误");
        addSystemMessage("连接错误", "无法连接到服务器");
      };

      const close = () => {
        console.log("socket已经关闭");
        addSystemMessage("连接断开", "与服务器的连接已断开");
      };

      const getMessage = (msg) => {
        const obj = JSON.parse(msg.data);
        console.log(obj);

        if (obj.type === "user_list") {
          users.value = obj.data.users_list;
        } else if (obj.type === "login") {
          addSystemMessage("用户加入", obj.message);
        } else if (obj.type === "logout") {
          const userIndex = users.value.indexOf(obj.data);
          if (userIndex > -1) {
            users.value.splice(userIndex, 1);
          }
          addSystemMessage("用户离开", obj.message);
        } else if (obj.type === "message") {
          addChatMessage(obj.user.username, obj.message, obj.user.datetime);
        }
        console.log(users.value);
      };

      const send = () => {
        if (!sendmsg.value || sendmsg.value.trim() === "") {
          console.log("发送的消息不能为空！");
          return;
        }
        if (socket.value && socket.value.readyState === WebSocket.OPEN) {
          socket.value.send(sendmsg.value);
          sendmsg.value = "";
        } else {
          addSystemMessage("发送失败", "连接已断开，无法发送消息");
        }
      };

      const addChatMessage = (username, msg, datetime) => {
        const messageObj = {
          content: `${username}: ${msg}`,
          time: datetime,
          isSystem: false
        };
        messages.value.push(messageObj);
        scrollToBottom();
      };

      const addSystemMessage = (type, content) => {
        const messageObj = {
          content: `[${type}] ${content}`,
          time: new Date().toLocaleTimeString(),
          isSystem: true
        };
        messages.value.push(messageObj);
        scrollToBottom();
      };

      const scrollToBottom = () => {
        nextTick(() => {
          if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
          }
        });
      };

      // 登出功能
      const logout = async () => {
        if (confirm('确定要退出聊天室吗？')) {
          try {
            // 关闭WebSocket连接
            if (socket.value) {
              socket.value.close();
            }
            
            // 调用登出接口
            const response = await fetch('/api/v1/user/logout_action', {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
              }
            });
            
            if (response.ok) {
              // 登出成功，跳转到登录页面
              window.location.href = '/login';
            } else {
              // 登出失败，仍然跳转到登录页面
              console.warn('登出接口调用失败，但仍跳转到登录页面');
              window.location.href = '/login';
            }
          } catch (error) {
            console.error('登出过程中发生错误:', error);
            // 即使出错也跳转到登录页面
            window.location.href = '/login';
          }
        }
      };

      // 显示用户菜单（可以扩展更多功能）
      const showUserMenu = () => {
        // 这里可以添加用户菜单功能，比如修改个人信息等
        console.log('用户菜单点击');
      };

      onMounted(() => {
        getCurrentUser();
        initSocket();
      });

      onUnmounted(() => {
        if (socket.value) {
          socket.value.close();
        }
      });

      return {
        title,
        users,
        messages,
        sendmsg,
        send,
        socket,
        messagesContainer,
        WebSocket,
        currentUser,
        logout,
        showUserMenu
      };
    },
  });
}

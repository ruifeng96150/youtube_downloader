export function Container() {
    let ws;
    return {
        url: '',
        data: [],
        name: '',
        hint: '',
        sendMsg(action, data = '') {
            ws.send(JSON.stringify({ action, data }))
        },
        initWs() {
            const that = this;
            ws = new WebSocket('ws://localhost:8000/ws');
            ws.onopen = function () {
                console.log('Connected to server');
                that.sendMsg('getlist', {})
            };
            ws.onmessage = function (event) {
                const resp = JSON.parse(event.data)
                console.log('Received message:', resp);

                switch (resp.action) {
                    case "getlist":
                        that.data = resp.data;
                        break;
                    case "downloading":
                        that.hint = "下载中";
                        break;
                    case "downloaded":
                        that.hint = ""
                        that.data = resp.data;
                        break
                }
            };
        },
        onSubmit(e) {
            e.preventDefault();
            console.log('jsonData', this.name, this.url)
            this.sendMsg('download', { name: this.name, url: this.url })
        },
        mounted() {
            console.log(`I'm mounted!`)
            this.initWs()
        }
    }
}
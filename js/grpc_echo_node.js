import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

app.registerExtension({
    name: "Comfy.GrpcEchoNode",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "GRPCEchoNode") {
            // Add a "Test Connection" button
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                const hostWidget = this.widgets.find((w) => w.name === "host");
                const certWidget = this.widgets.find((w) => w.name === "cert_path");

                this.addWidget("button", "⚡ Test Connection", null, () => {
                    // Feedback to user
                    const originalText = "⚡ Test Connection";
                    const buttonWidget = this.widgets.find(w => w.label === originalText || w.name === "Test Connection");
                    if (buttonWidget) buttonWidget.label = "⌛ Testing...";

                    api.fetchApi("/comfyui-grpc/test_connection", {
                        method: "POST",
                        body: JSON.stringify({
                            host: hostWidget.value,
                            cert_path: certWidget.value
                        }),
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (buttonWidget) buttonWidget.label = originalText;
                            if (data.success) {
                                alert("✅ Connection Successful!\n\n" + data.message);
                            } else {
                                alert("❌ Connection Failed\n\n" + data.message);
                            }
                        })
                        .catch(error => {
                            if (buttonWidget) buttonWidget.label = originalText;
                            alert("❌ Request Error: " + error);
                        });
                });

                return r;
            };
        }
    },
});


var mrpc = function(prefix) {
    function proxy(prefix) {
        this.prefix = prefix;
        this.rpc = function rpc(path, procedure, value) {
            var data = {
                path: path,
                procedure: procedure,
                value: value
            }
            return $.ajax({
                url: prefix + "/rpc",
                dataType: "json",
                contentType: "application/json",
                method: "POST",
                data: JSON.stringify(data)
            });
        }
    }
    return new proxy(prefix);
}
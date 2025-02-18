function getCookie(name) {
    // https://docs.djangoproject.com/en/4.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false

    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function beautify_device_status_update(device_ref, tooltip_content) {
    let last_update_status = `#${device_ref}-last_update_status`;
    let img_new_html = '<i class="bi bi-question-circle h3"></i>';
    let img_success_html = '<i class="bi bi-check-circle h3"></i>';
    let img_failure_html = '<i class="bi bi-exclamation-circle h3"></i>';

    switch ($(last_update_status).text().trim()) {
        case 'NEW':
            $(last_update_status).html(img_new_html);
            break;
        case 'SUCCESS':
            $(last_update_status).html(img_success_html);
            break;
        default:
            $(last_update_status).html(img_failure_html);
    }

    $(last_update_status).attr("title", tooltip_content);
}

function update_device_status(device_ref, fields_to_update, api_url) {
    let auto_update_flag = getCookie('auto_update_flag');
    if(auto_update_flag == null || auto_update_flag === 'true' ) {
        $.ajax({
            type: 'POST',
            url: api_url,
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            mode: 'same-origin',
            success: function(response){
                for (let field of fields_to_update) {
                    let response_field = response[field];
                    if (response_field instanceof Object) {
                        for (let [key, value] of Object.entries(response_field)) {
                            let field_to_update = $(`#${device_ref}-${field}-${key}`);
                            let updater_name = field_to_update.attr('data-updater');
                            if (updater_name !== undefined) {
                                FieldUpdaters[updater_name](field_to_update, value)
                            } else {
                                field_to_update.text(value);
                            }
                        }
                    } else {
                        $(`#${device_ref}-${field}`).text(response_field);
                    }
                }

                beautify_device_status_update(device_ref, response["last_status_update_log"]);
            },
            error: function(response){
                console.log(`API ERROR => ${response}`)
            }
        });
    } else {
        console.log("Auto-update is disabled by the cookie!");
    }
}

function change_device_status(update_data, success_function, error_function, api_url) {
    $.ajax({
        type: 'POST',
        url: api_url,
        data: update_data,
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        mode: 'same-origin',
        success: success_function,
        error: error_function,
    });
}

function update_checkbox(field, value) {
    field.prop("checked", value);
}

function change_checkbox(field, api_url) {
    function success(response) {
        field.prop("checked", field.checked);
    }

    function error(response) {
        field.prop("checked", !field.checked);
    }

    change_device_status({"active": field.checked}, success, error, api_url);
}

let FieldUpdaters = {
    "update_checkbox": update_checkbox,
};

let FieldChangers = {
    "change_checkbox": change_checkbox,
};

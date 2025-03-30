jQuery.fn.exists = function(){return this.length>0;}

/* Common utilities */

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

/* Utilities for Devices */

function update_device_details(device_ref, updated_data) {
    for (let [field_name, field_value] of Object.entries(updated_data)) {
        if (field_value instanceof Object) {
            for (let [key, value] of Object.entries(field_value)) {
                let field_to_update = $(`#${device_ref}-${field_name}-${key}`);
                if (field_to_update.exists()) {
                    let updater_name = field_to_update.attr('data-updater');
                    if (updater_name !== undefined) {
                        FieldUpdaters[updater_name](field_to_update, value)
                    } else {
                        field_to_update.text(value);
                    }
                }
            }
        } else {
            $(`#${device_ref}-${field_name}`).text(field_value);
        }
    }
}

function beautify_device_status(device_ref, updated_data) {
    let last_update_status = $(`#${device_ref}-last_update_status`);
    let img_new_html = '<i class="bi bi-question-circle h3"></i>';
    let img_success_html = '<i class="bi bi-check-circle h3"></i>';
    let img_failure_html = '<i class="bi bi-exclamation-circle h3"></i>';

    switch (updated_data['last_update_status']) {
        case 'NEW':
            last_update_status.html(img_new_html);
            break;
        case 'SUCCESS':
            last_update_status.html(img_success_html);
            break;
        default:
            last_update_status.html(img_failure_html);
    }

    last_update_status.attr("title", updated_data["last_status_update_log"]);
}

function render_device_status(device_ref, updated_data) {
    update_device_details(device_ref, updated_data)
    beautify_device_status(device_ref, updated_data);
}


function read_device_status(device_ref, api_url, http_method = 'GET', data = {}) {
    let GET_data = JSON.stringify(data)
    $.ajax({
        type: http_method,
        url: api_url,
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        data: (GET_data !== "{}") ? GET_data: null,
        contentType: 'application/json',
        mode: 'same-origin',
        success: function(response){
            render_device_status(device_ref, response);
        },
        error: function(response){
            console.log(`API CALL ERROR => ${JSON.stringify(response)}`);
            render_device_status(device_ref, response["responseJSON"]);
        }
    });
}

function change_device_status(api_url, update_data, success_function, error_function) {
    $.ajax({
        type: 'POST',
        url: api_url,
        data: JSON.stringify(update_data),
        contentType: 'application/json',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        mode: 'same-origin',
        success: success_function,
        error: error_function,
    });
}

function register_auto_update(read_status_params) {
    let auto_update_flag = getCookie('auto_update_flag');
    if(auto_update_flag == null || auto_update_flag === 'true' ) {
        $(window).on('load', function() {
            read_device_status.apply(this, read_status_params);
        });
    } else {
        console.log("Auto-update is disabled by the cookie!");
    }
}

function register_refresh_button(button_name, read_status_params) {
    $(document).ready( function() {
        $(button_name).click(function () {
            read_device_status.apply(this, read_status_params);
        });
    });
}

/* Utilities for fields */

function update_checkbox(field, value) {
    field.prop("checked", value);
}

function change_checkbox(device_ref, field, post_data, api_url) {
    function success(response) {
        render_device_status(device_ref, response);
    }

    function error(response) {
        console.log(`API CALL ERROR => ${JSON.stringify(response)}`);
        field.prop("checked", !field.prop("checked"));
        render_device_status(device_ref, response["responseJSON"]);
    }

    change_device_status(api_url, post_data, success, error);
}

let FieldUpdaters = {
    "update_checkbox": update_checkbox,
};

let FieldChangers = {
    "change_checkbox": change_checkbox,
};

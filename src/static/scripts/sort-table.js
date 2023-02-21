let pickup_data = null

function slider_update(el, output_el) {
    document.getElementById(output_el).value = el.value + ' mm';
}

function apply_filter() {
    filter = document.getElementById('filter');
    Array.from(filter.getElementsByTagName('input')).forEach((instance) => {
        if(instance.name.includes('brand-')) {
            if(instance.checked) {
                console.log(instance)
            }
        }
    })
}

function load_json(url) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
        pickup_data = JSON.parse(xhr.responseText);
    }};

    xhr.send();
};
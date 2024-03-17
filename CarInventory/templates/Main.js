let input1 = document.getElementById('from')
let input2 = document.getElementById('to')

let autocomplete1 = new google.maps.places.Autocomplete(input1)
let autocomplete2 = new google.maps.places.Autocomplete(input2)

let myLatLng = {
    lat:38.346,
    lng:1.355
}

let mapOptions = {
    center: myLatLng,
    zoom: 7,
    mapTypeId: google.maps.MapTypeId.ROADMAP
}

let map = new google.maps.Map(document.getElementById("googleMap"),mapOptions)

var directionService = new google.maps.DirectionsService();

var directiondisplay = new google.maps.DirectionsRenderer();

directiondisplay.setMap(map);

function calcRoute(){
    let request = {
        origin:document.getElementById("from").value,
        destination:document.getElementById("to").value,
        travelMode: google.maps.TravelMode.DRIVING,
    }

    directionService.route(request, function(result,status){
        if(status == google.maps.DirectionStatus.OK){
            const output = document.querySelector("#output");
            output.innerHTML = 
            "<div class='alert alert-info'> From: " + 
            document.getElementById('from').value + 
            ".<br/> To: " + 
            document.getElementById('to').value + 
            ".<br/> Driving distance <i class = 'fa fa-road'></i>:" +
            result.routes[0].legs[0].distance.text + 
            ".<br/> Duration < i class = 'fas fa-hourglass-start'> </i> :" +
            result.routes[0].legs[0].duration.text + 
            " .</div> ";
            directiondisplay.setDirections(result) 
        }
        else {
            const output = document.querySelector("#output");
            output.innerHTML = "<div class='alert alert-danger'>Unable to find a route.</div>";
        }
    })
}
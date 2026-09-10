let fondos = [
    "../static/Imagenes/13.jpg",
    "../static/Imagenes/10.jpg",
    "../static/Imagenes/11.jpg",
    "../static/Imagenes/12.jpg"
];

let posicion = 0;

setInterval(function(){
    posicion++;

    if(posicion >= fondos.length){
        posicion = 0;
    }

    document.body.style.backgroundImage = "url('" + fondos[posicion] + "')";
}, 5000);
function copiarCorreo(event) {
    event.preventDefault();

    const correo = "itindpiloto6@educacionbogota.edu.co";

    navigator.clipboard.writeText(correo)
        .then(() => {
            alert("Correo copiado: " + correo);
        })
        .catch(() => {
            alert("No se pudo copiar el correo");
        });
}

document.addEventListener("DOMContentLoaded", function () {

    let botonMenu = document.getElementById("botonMenu");
    let menu = document.getElementById("menuDesplegable");

    botonMenu.addEventListener("click", function (event) {

        event.preventDefault();

        menu.classList.toggle("mostrar");

    });

});
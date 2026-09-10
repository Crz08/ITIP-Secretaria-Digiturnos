let fondos = [
    "../static/Imagenes/6.jpg",
    "../static/Imagenes/1.jpg",
    "../static/Imagenes/2.jpg",
    "../static/Imagenes/29.jpg"
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

    let correo = "itindpiloto6@educacionbogota.edu.co";

    let texto = document.createElement("textarea");
    texto.value = correo;

    document.body.appendChild(texto);
    texto.select();

    document.execCommand("copy");

    document.body.removeChild(texto);

    alert("Correo copiado");
}

document.addEventListener("DOMContentLoaded", function () {

    let botonMenu = document.getElementById("botonMenu");
    let menu = document.getElementById("menuDesplegable");

    botonMenu.addEventListener("click", function (event) {

        event.preventDefault();

        menu.classList.toggle("mostrar");

    });

});
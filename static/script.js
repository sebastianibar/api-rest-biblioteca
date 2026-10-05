// Funciones para cargar datos iniciales
function cargarDatos() {
    cargarAutores();
    cargarLibros();
}

//Apartado de autores
function cargarAutores() {
    fetch('/autores')
        .then(res => res.json())
        .then(data => {
            // Actualizar la lista en HTML
            let lista = document.getElementById('lista-autores');
            let select = document.getElementById('libro-autor-id');
            
            lista.innerHTML = '';
            select.innerHTML = '<option value="">Selecciona un Autor</option>'; // Limpiar opciones

            data.forEach(a => {
                // Agregar a la lista
                lista.innerHTML += `<li>ID: ${a.id} - ${a.nombre} (${a.nacionalidad}) 
                    <button class="btn-delete" onclick="eliminarAutor(${a.id})">Eliminar</button></li>`;
                
                // Agregar al desplegable de libros
                select.innerHTML += `<option value="${a.id}">${a.nombre}</option>`;
            });
        })
        .catch(err => console.error("Error al cargar autores:", err));
}

function agregarAutor() {
    let nombre = document.getElementById('autor-nombre').value;
    let nacionalidad = document.getElementById('autor-nac').value;

    fetch('/autores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, nacionalidad })
    })
    .then(res => res.json())
    .then(data => {
        if(data.error) alert("Error: " + data.error);
        cargarDatos(); // Recargar todo para actualizar desplegables
    });
}

function eliminarAutor(id) {
    if(!confirm("¿Seguro que deseas eliminar este autor? Sus libros también podrían verse afectados.")) return;
    
    fetch(`/autores/${id}`, { method: 'DELETE' })
        .then(() => cargarDatos());
}

//Apartado de libros
function cargarLibros() {
    fetch('/libros')
        .then(res => res.json())
        .then(data => {
            let lista = document.getElementById('lista-libros');
            lista.innerHTML = '';
            data.forEach(l => {
                lista.innerHTML += `<li>${l.titulo} (${l.anio}) - Autor: ${l.autor}
                    <button class="btn-delete" onclick="eliminarLibro(${l.id})">Eliminar</button></li>`;
            });
        });
}

function agregarLibro() {
    let titulo = document.getElementById('libro-titulo').value;
    let anio = document.getElementById('libro-anio').value;
    let autor_id = document.getElementById('libro-autor-id').value;

    if(!autor_id) {
        alert("Por favor selecciona un autor");
        return;
    }

    fetch('/libros', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo: titulo, anio: parseInt(anio), autor_id: parseInt(autor_id) })
    })
    .then(res => res.json())
    .then(data => {
        if(data.error) alert("Error: " + data.error);
        cargarLibros();
    });
}

function eliminarLibro(id) {
    fetch(`/libros/${id}`, { method: 'DELETE' })
        .then(() => cargarLibros());
}

// Ejecutar al iniciar la página
window.onload = cargarDatos;
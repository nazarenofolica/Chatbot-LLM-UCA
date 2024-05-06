#imports de librerias necesarias
import openai   # Interactuar con la API de chatgpt
import streamlit as st #interfaz
import time            #temporizadores
import pymysql         #conexion con mysql

# Configuración de la API Key
api_key = "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"
openai.api_key = api_key

# Función para la interacción con el chatbot
def chatbot_interaction(memory, query, first_interaction):
    if first_interaction: #si es la primer interaccion usa prompt 1(usa el nombre de la memoria)
        prompt = [
            {"role": "assistant", "content": "Haz el rol de un chatbot el cual brinda información a aquellos que estén interesados en la carrera universitaria licenciatura en ciencia de datos. Tu objetivo es utilizar técnicas de marketing para buscar que los interesados quieran elegir la carrera. Siempre al principio de cada respuesta tienes que utilizar su nombre. Pon un conector luego del nombre para que sea más natural la respuesta. En la respuesta debes brindar la información en base a las preferencias del interesado, como por ejemplo si quiere una respuesta más divertida o seria, o si quiere una respuesta más concisa o creativa. Además, la respuesta debe adaptarse al nivel de conocimiento que tiene el interesado basado en la información del perfil del usuario, por ejemplo si tiene un conocimiento avanzado, intermedio o bajo, o si su educación es nivel secundario, nivel universitario o nivel posgrado. Finalizar preguntando al usuario si tiene alguna consulta más . No quiero que mezcles la información del perfil con la de la consulta y tampoco quiero que hagas afirmaciones que sé desvíen de la consulta."},
            {"role":  "user", "content": f" hola mi nombre es {memory['name']} y soy un interesado. Quiero que me respondas y me brindes información de esta pregunta: {query['question']}, utilizando técnicas de marketing para que elija la carrera. Para responder esa pregunta quiero que te inspires con esta información: {query['answer']}. Además, quiero que lo expliques considerando mi conocimiento que tengo sobre el campo, el cual es de nivel {memory['grade']}. También, quiero que me lo expliques según el nivel de educación que tengo, el cual es de nivel {memory['education']}. Por último, quiero que me respondas con un sentimiento {memory['state']}"}]

    else: #sino, prompt 2(no repite nombre)
        prompt = [
            {"role": "assistant", "content": "Haz el rol de un chatbot el cual brinda información a aquellos que estén interesados en la carrera universitaria licenciatura en ciencia de datos. Tu objetivo es utilizar técnicas de marketing para buscar que los interesados quieran elegir la carrera. Pon un conector luego del nombre para que sea más natural la respuesta. En la respuesta debes brindar la información en base a las preferencias del interesado, como por ejemplo si quiere una respuesta más divertida o seria, o si quiere una respuesta más concisa o creativa. Además, la respuesta debe adaptarse al nivel de conocimiento que tiene el interesado basado en la información del perfil del usuario, por ejemplo si tiene un conocimiento avanzado, intermedio o bajo, o si su educación es nivel secundario, nivel universitario o nivel posgrado. Finalizar preguntando al usuario si tiene alguna consulta más. No quiero que mezcles la información del perfil con la de la consulta y tampoco quiero que hagas afirmaciones que sé desvíen de la consulta."},
            {"role":  "user", "content": f" Quiero que empieces la conversacion con un saludo más un conector de manera original, siendo asi que es levemente probable que se repita luego. Quiero que empieces la conversacion con un saludo más un conector de manera original, siendo asi que es levemente probable que se repita luego, quiero que este saludo lo generes segun el {memory['state']}, por ejemplo siendo el state serio un saludo cordial, siendo divertido uno amistoso y siendo normal uno normal. Quiero que me respondas y me brindes información de esta pregunta: {query['question']}, utilizando técnicas de marketing para que elija la carrera. Para responder esa pregunta quiero que te inspires con esta información: {query['answer']}. Además, quiero que lo expliques considerando mi conocimiento que tengo sobre el campo, el cual es de nivel {memory['grade']}. También, quiero que me lo expliques según el nivel de educación que tengo, el cual es de nivel {memory['education']}. Por último, quiero que me respondas con un sentimiento {memory['state']}"}]
    #Agregar unidad de memoria para que cambie el saludo todo el tiempo luego del boton de la consulta.   
    response = openai.ChatCompletion.create(  #genero respuesta a partir de chatgpt
        model="gpt-3.5-turbo-0125",           #version
        temperature = memory["temperature"],  #creatividad del modelo
        max_tokens = memory["token"],         #cantidad de texto
        messages= prompt                      #estructura de respuesta e indicaciones
    )
    res = response.choices[0].message.content #asigno respuesta generada a variable

    return res  #retorno


def Question(id_question, cursor):
    cursor.execute("Select * from Question;") #crea cursor para interactuar con la base de datos de mysql
    questions = cursor.fetchall() #selecciona todas las filas de la base de datos y las guarda en la variable question

    url = None     #sin url cargada     
    flag = False   #bandera
    i=0            #contador
    while flag == False and i < len(questions):   #mientras que sea menor que la cantidad de filas y la bandera sea falsa
        if questions[i][0] == id_question: #si la fila i tiene mismo id que la question de la consulta hecha por el usuario
            question = questions[i][2]     #pregunta es la pregunta predefinida
            answer = questions[i][3]       #respuesta predefinida
            flag = True                    #cierro cicloc
            url = questions[i][4]          #link de ayuda extra
        else:
            i+=1                           #si no coincide id, busco la siguiente fila

    query = {"question": question, "answer": answer, "id_question": id_question, "url": url} #diccionario con la informacion de la consulta 
    return query #devuelvo ese diccionario

def get_id_question(option, sub_option):
    query_option_dict = {"🤔 ¿Cuánto vale la mensualidad?": 1, "🤖 ¿De qué trata la carrera de la Licenciatura en Ciencia de Datos?": 2,
                                     "📄 ¿Cuál es el plan de estudio y la duración de la carrera?": 3, "💼 ¿Cuáles son las aplicaciones laborales?": {"🚑 Sector Médico": 4, "💹 Sector Económico": 5, "🎨 Sector Artístico": 6, "🏢 Sector Empresarial": 7},
                                     "🏢 Información Laboratorio de Ciencia de Datos": {"🤔 ¿Que es el laboratorio de ciencia de datos?": 8, "🔍 ¿Qué puedo encontrar en el laboratorio?": 9, "📄 ¿Cuáles son las normas de convivencia?": 10, "👥 ¿Quienes estan a cargo del laboratorio?": 11},
                                     "💻 ¿Que habilidades se desarrollan en la carreras?": 12} #diccionario que segun consulta devuelve el id en sql (introduce pregunta saca id)

    if option in query_option_dict:   #si la opcion esta entre las posibles
        id_question = query_option_dict.get(option) #obtengo el id o valor y lo guardo en id question 
        if type(id_question) == dict: #si el valor es de tipo diccionario significa que tiene subpreguntas
            if sub_option in id_question:
                id_question = id_question.get(sub_option) #busca la subpregunta en el id question
            else:
                id_question = None #si no esta devuelve error(no hay seleccion)
        else:
            pass #pasa porque no hay subpreguntas y el id question esta asignado
    else:
        id_question = None #si no hay seleccion devuelve error
    
    return id_question #retorno el id question


# Función principal para la aplicación web
def main():
    
    hide_menu_style = """             
    <style>
    header {visibility: hidden; }
    </style>
    """                             #formato html para que no se pueda interactuar con opciones de apariencia

    st.markdown(hide_menu_style, unsafe_allow_html=True) #ejecuto la secuencia html para efectuar los cambios

    st.title("🤖 ChatBot + LLM sobre la Licenciatura en Ciencia de Datos") #titulo de la pagina
    st.markdown("Este chatbot está diseñado para brindar información sobre la Licenciatura en Ciencia de Datos. Las respuestas son generados con Inteligencia Artificial, por lo que si no son coherentes te recomendamos que vuelvas a preguntar. Antes de empezar te pido que ingreses algunos datos para que la respuesta sea personalizada segun tus preferencias y conocimiento.") #descripcion de la pagina

    host =  'chatbotdb.chaxaoxmo9uf.us-east-1.rds.amazonaws.com'  #host de la base de datos
    port = 3306                                                   #puerto(mysql es 3306)
    user = 'admin'                                                #usuario de la base de datos
    password = 'chatbotUCA2024'                                   #contraseña
    database = 'ChatBot'                                        #nombre de la base de datos

    try:
        connection = pymysql.connect(host=host, port=port , user= user, passwd = password, db= database) #intento la conexion

    except:
        print("Error de conexion") #notifico error


    with st.chat_message(name="assistant", avatar = "https://i.ibb.co/hBymPw0/image-removebg-preview.png"):
        memory = {}
        name = st.text_input("Cuál es tu nombre?")
        memory['name'] = name                          #obtengo nombre usuario
    
    with st.chat_message(name="assistant",avatar="https://i.ibb.co/hBymPw0/image-removebg-preview.png"): # Crear un formulario para agrupar los widgets de selección
        with st.form(key="form"):
            education_options = ["Seleccione opción", "🎓 Educación secundaria", "🎓 Licenciatura / Grado universitario", "🎓 Postgrado / Maestría / Doctorado"]
            education = st.selectbox("🎓 ¿Cuál es tu nivel de educación más alto alcanzado hasta ahora?", education_options)
            memory['education'] = education[2:]    #obtengo nivel de educacion

            grade_options = ["Seleccione opción", "⚪ Principiante (sin experiencia previa)", "🟡 Intermedio (alguna experiencia, pero limitada)", "🟠 Avanzado (amplia experiencia)"]
            grade = st.selectbox("💻 ¿Cuál es tu nivel de experiencia en el campo de la carrera que estás explorando?", grade_options)
            memory['grade'] = grade[2:]   #obtengo nivel experiencia

            token_temperature_options = ["Seleccione opción", "🔵 Más concisas", "⚪ Equilibrado", "🔴 Más creativas"]
            token_temperature = st.selectbox("✏ Elige estilo de respuesta.", token_temperature_options)  #niveles de creatividad

            token_temperature_dict = {"🔵 Más concisas": (270, 0.4), "⚪ Equilibrado": (300, 0.9), "🔴 Más creativas": (400, 1.3)} #establezco niveles de temperatura segun creatividad

            token = 300
            temperature = 0.9

            if token_temperature != "Seleccione opción":
                token_temperature_tuple = token_temperature_dict.get(token_temperature)
                token = token_temperature_tuple[0]
                temperature = token_temperature_tuple[1]     #establezco niveles de temperatura segun creatividad

            memory['token'] = token
            memory['temperature'] = temperature      #guardo los tokens en memoria para pasarlo en el prompt


            state_options = ["Seleccione opción", "😃 Divertida", "🙂 Normal", "😐 Seria"]
            state = st.selectbox("😃 ¿Como quieres que sea la conversacion?", state_options)
            memory['state'] = state[2:]       #establezco nivel de seriedad

            query_option = st.selectbox("🤔 Elige una consulta.",
                                    ["Seleccione opción",
                                     "🤔 ¿Cuánto vale la mensualidad?",
                                     "🤖 ¿De qué trata la carrera de la Licenciatura en Ciencia de Datos?",
                                     "📄 ¿Cuál es el plan de estudio y la duración de la carrera?",
                                     "💼 ¿Cuáles son las aplicaciones laborales?",
                                     "🏢 Información Laboratorio de Ciencia de Datos",
                                     "💻 ¿Que habilidades se desarrollan en la carreras?"])   #se selecciona la consulta       
            
            sub_questions = {
                "Seleccione opción": "",
                "🤔 ¿Cuánto vale la mensualidad?": "",
                "🤖 ¿De qué trata la carrera de la Licenciatura en Ciencia de Datos?": "",
                "📄 ¿Cuál es el plan de estudio y la duración de la carrera?": "",
                "💼 ¿Cuáles son las aplicaciones laborales?": ["Seleccione sector", "🚑 Sector Médico", "💹 Sector Económico", "🎨 Sector Artístico", "🏢 Sector Empresarial"],
                "🏢 Información Laboratorio de Ciencia de Datos": ["Seleccione opción","🤔 ¿Que es el laboratorio de ciencia de datos?", "🔍 ¿Qué puedo encontrar en el laboratorio?", "📄 ¿Cuáles son las normas de convivencia?", "👥 ¿Quienes estan a cargo del laboratorio?"],
                "💻 ¿Que habilidades se desarrollan en la carreras?": ""
            } #se selecciona una subconsulta pata los casos necesarios

            subquery_option = st.selectbox("Algunas preguntas tienen sub-preguntas", sub_questions[query_option]) #creo la caja de seleccion de las preguntas

        # Crear un botón de envío para el formulario
            submitted = st.form_submit_button("Hacer consulta") #boton para enviar las consultas

        if submitted: #Si el botón se presiona, verificar si todas las opciones son válidas
            completed = True  #Crear una variable booleana para indicar si el usuario ha completado todas las opciones

        # Si alguna opción es "Seleccione opción", cambiar el valor de la variable a False y mostrar un mensaje de error
            option = (name, education, grade, token_temperature, state, query_option) 
            errors = ("Por favor, escribe tu nombre.", "Por favor, elige tu nivel de educación.", 
                      "Por favor, elige tu nivel de experiencia.", "Por favor, elige el estilo de respuesta.", 
                      "Por favor, elige el tono de la conversación.", "Por favor, elige una consulta válida.") #tipos de errores segun campo incompleto
            i = 0
            while i < len(option):   #mientras el contador sea menor a la cantidad de opciones
                if option[i] == "Seleccione opción" or option[i] == "": #si no hay seleccion o el nombre esta vacio
                    st.error(errors[i])  #imprime el error correspondiente
                    completed = False #cambio la variable booleana
                i+=1 #veo la siguiente opcion si esta completa la anterior

            if completed: #Si todas las opciones son válidas, procesar la consulta normalmente
                    query = {} #creo dicc vacio
                    flag = True #bandera positiva

                    cursor = connection.cursor() #creo cursor 

                    id_question = get_id_question(query_option, subquery_option) #obtengo la id de la pregunta con la funcion de arriba
                    if id_question is not None:
                        query = Question(id_question, cursor) #la pregunta se obtiene con la funcion de arriba que recibe el id y el cursor
                    else: # Si el usuario elige "Seleccione sector"
                            flag = False #termino el ciclo
                            if 'query_prev' not in st.session_state:  #si la pregunta previa no esta en la sesion
                                st.session_state['query_prev'] = ""   #creo la pregunta previa y le asigno caracter vacio
                            if 'contador' not in st.session_state:    #si hay contador
                                st.session_state['contador'] = 0      #es creado si no existe
                            if query_option != st.session_state['query_prev']:     #si la pregunta actual es diferente a la anterior
                                st.session_state['contador'] = 0      #vuelvo el contador a cero
                            if submitted:                             #si se hizo la consulta
                                st.session_state['contador'] += 1     #sumo 1 al contador
                            if st.session_state['contador'] > 1:      #si contador es mayor a 1
                                st.error("Por favor, elige una consulta válida.")   #mensaje de error para que se seleccione la subconsulta
                                del st.session_state['contador']      #borra el contador
                    st.session_state['query_prev'] = query_option     #establezco la pregunta actual como la previa para no repetirla

                    if 'first_interaction' not in st.session_state:   #si es la primer interaccion
                        st.session_state['first_interaction'] = True  #la creo para que quede establecida

                    if flag: #si la bandera es positiva
                        response = chatbot_interaction(memory, query, st.session_state['first_interaction']) #creo la respuesta con la funcion de chatgpt
            
                        st.session_state['first_interaction'] = False # Actualizar el valor del session state a False

                    
                        image_html = """
                        <img src="https://i.ibb.co/hBymPw0/image-removebg-preview.png" style="width:50px; height:50px; margin-left:-14px">
                        """  #imagen para la interfaz

                        #Crear el contenedor con el título y la imagen
                        container_html = f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        {image_html}
                        <h1 style="text-align: left; font-size: 22px; vertical-align: middle; font-weight: bold; margin-left: 1px; color: black; ">L.U.C.A</h1>
                        </div>
                        """

                        st.components.v1.html(container_html, height=100) #Mostrar el contenedor usando la función st.components.v1.html
                        if query["url"] != None: #si tiene url
                            response+= f"\nSi tienes alguna consulta más sobre este tema, podes hacer clic en el botón de abajo." #respuesta para poner el link
                        
                        #'ChatBot-AI-main\L.U.C.A.jpg'
                        text = "" # Inicializar el texto vacío
                        placeholder = st.empty() # Crear un marcador de posición vacío
                        for char in response: #si caracter en respuesta
                            text += char # Agregar el carácter actual al texto
                            placeholder.markdown(f"<p style=\"margin-top:-60px;\">{text}</p>", unsafe_allow_html=True) # Escribir el texto actual en el marcador de posición
                            time.sleep(0.01) # Esperar 0.01 segundos
                        placeholder.markdown(f"<p style=\"margin-top:-60px;\">{response}</p>", unsafe_allow_html=True) # Escribir el texto completo en el marcador de posición
                        if query["url"] != None: #si tiene url
                            st.link_button("Ir a la página web", url= query["url"]) #Si tienes alguna consulta más sobre este tema, podes hacer clic en el botón de abajo.
                            

    with st.chat_message(name="assistant", avatar = "https://i.ibb.co/hBymPw0/image-removebg-preview.png"): #mensaje con el formato de asistente e imagen de avatar
        with st.form(key="form2"): #forma de la respuesta
            st.write("Para enviar su calificación complete al menos un campo.") #mensaje al usuario sobre la calificacion
            star_option = st.selectbox("⭐ Califica al ChatBot del 1 al 5", ["Seleccione opción","⭐ 1","⭐ 2","⭐ 3","⭐ 4","⭐ 5"]) #caja de seleccion para las estrellas
            new_question = st.text_input("✏ ¿Qué pregunta te gustaria añadir?") #input para nuevas preguntas

            submitted_2 = st.form_submit_button("Enviar") #boton de enviar reviews

        if submitted_2:  #si se envio
            completed_2 = True #completado es verdadero(bandera)

            if star_option == "Seleccione opción": #si la estrella es igual a seleccione opcion
                completed_2 = False                #no se completo
                st.error("Por favor, rellene al menos un campo.") #mensaje error
        
            if completed_2:
                insert = connection.cursor() #creo cursor llamado insert

                star_dict = {"⭐ 1": 1, "⭐ 2": 2, "⭐ 3": 3, "⭐ 4": 4, "⭐ 5": 5} #valores de las estrellas

                star = star_dict.get(star_option) #Obtener el valor de star usando el diccionario

                if new_question == "": #si pregunta es vacia
                    new_question = None #pregunta nueva es nula en sql

                review = {"star": star, "new_question": new_question} #diccionario con los valores de la review

                if new_question == None: #si pregunta es nula 
                    query_insert = f"INSERT INTO Review(name, star, new_question) VALUES ('{memory['name']}', {review['star']}, NULL)" #inserto en sql el nombre y las estrellas
                else: #sino
                    query_insert = f"INSERT INTO Review(name, star, new_question) VALUES ('{memory['name']}', {review['star']}, '{review['new_question']}')" #inserto nombre, estrellas y pregunta
                
                insert.execute(query_insert) #ejecuto el cursor con las variables anteriores
                connection.commit()          #confirmo la ejecucion
                insert.close()               #cierro el cursor

                st.success("Enviado con éxito") #mensaje de exito


    connection.close() #cierro la conexion

main() #llamo a la funcion main para ejecutar el codigo
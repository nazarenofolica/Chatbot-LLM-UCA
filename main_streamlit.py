import openai   # Interactuar con la API de chatgpt
import streamlit as st
import time
import pymysql

# Configuración de la API Key
api_key = "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"

openai.api_key=api_key

# Función para la interacción con el chatbot
def chatbot_interaction(memory, query, first_interaction):
    if first_interaction:
        prompt = [
            {"role": "assistant", "content": "Haz el rol de un chatbot el cual brinda información a aquellos que estén interesados en la carrera universitaria licenciatura en ciencia de datos. Tu objetivo es utilizar técnicas de marketing para buscar que los interesados quieran elegir la carrera. Siempre al principio de cada respuesta tienes que utilizar su nombre. Pon un conector luego del nombre para que sea más natural la respuesta. En la respuesta debes brindar la información en base a las preferencias del interesado, como por ejemplo si quiere una respuesta más divertida o seria, o si quiere una respuesta más concisa o creativa. Además, la respuesta debe adaptarse al nivel de conocimiento que tiene el interesado basado en la información del perfil del usuario, por ejemplo si tiene un conocimiento avanzado, intermedio o bajo, o si su educación es nivel secundario, nivel universitario o nivel posgrado. Finalizar preguntando al usuario si tiene alguna consulta más . No quiero que mezcles la información del perfil con la de la consulta y tampoco quiero que hagas afirmaciones que sé desvíen de la consulta."},
            {"role":  "user", "content": f" hola mi nombre es {memory['name']} y soy un interesado. Quiero que me respondas y me brindes información de esta pregunta: {query['question']}, utilizando técnicas de marketing para que elija la carrera. Para responder esa pregunta quiero que te inspires con esta información: {query['answer']}. Además, quiero que lo expliques considerando mi conocimiento que tengo sobre el campo, el cual es de nivel {memory['grade']}. También, quiero que me lo expliques según el nivel de educación que tengo, el cual es de nivel {memory['education']}. Por último, quiero que me respondas con un sentimiento {memory['state']}"}]

    else:
        prompt = [
            {"role": "assistant", "content": "Haz el rol de un chatbot el cual brinda información a aquellos que estén interesados en la carrera universitaria licenciatura en ciencia de datos. Tu objetivo es utilizar técnicas de marketing para buscar que los interesados quieran elegir la carrera. Pon un conector luego del nombre para que sea más natural la respuesta. En la respuesta debes brindar la información en base a las preferencias del interesado, como por ejemplo si quiere una respuesta más divertida o seria, o si quiere una respuesta más concisa o creativa. Además, la respuesta debe adaptarse al nivel de conocimiento que tiene el interesado basado en la información del perfil del usuario, por ejemplo si tiene un conocimiento avanzado, intermedio o bajo, o si su educación es nivel secundario, nivel universitario o nivel posgrado. Finalizar preguntando al usuario si tiene alguna consulta más. No quiero que mezcles la información del perfil con la de la consulta y tampoco quiero que hagas afirmaciones que sé desvíen de la consulta."},
            {"role":  "user", "content": f" Quiero que empieces la conversacion con un saludo más un conector de manera original, siendo asi que es levemente probable que se repita luego. Quiero que empieces la conversacion con un saludo más un conector de manera original, siendo asi que es levemente probable que se repita luego, quiero que este saludo lo generes segun el {memory['state']}, por ejemplo siendo el state serio un saludo cordial, siendo divertido uno amistoso y siendo normal uno normal. Quiero que me respondas y me brindes información de esta pregunta: {query['question']}, utilizando técnicas de marketing para que elija la carrera. Para responder esa pregunta quiero que te inspires con esta información: {query['answer']}. Además, quiero que lo expliques considerando mi conocimiento que tengo sobre el campo, el cual es de nivel {memory['grade']}. También, quiero que me lo expliques según el nivel de educación que tengo, el cual es de nivel {memory['education']}. Por último, quiero que me respondas con un sentimiento {memory['state']}"}]
    #Agregar unidad de memoria para que cambie el saludo todo el tiempo luego del boton de la consulta.   
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        temperature = memory["temperature"],
        max_tokens = memory["token"],
        messages= prompt
    )
    res = response.choices[0].message.content

    return res

def links(query):
    if query['id_question'] == 1:
        url = "https://autogestion.uca.edu.ar/aranceles"
        url_state=True
    elif query['id_question'] == 2:
        url = "https://www.youtube.com/watch?si=xC08s8_BOla2wwSj&embeds_referring_euri=https%3A%2F%2Fwww.bing.com%2F&embeds_referring_origin=https%3A%2F%2Fwww.bing.com&source_ve_path=Mjg2NjQsMTY0NTA2&feature=emb_share&v=gLXXoOa10E0"
        url_state=True
    elif query['id_question'] == 3:
        url = "https://uca.edu.ar/es/facultades/facultad-de-quimica-e-ingenieria-del-rosario/carrera-de-grado/licenciatura-en-ciencias-de-datos?sede_de_interes=Buenos%20Aires&carreras_de_grado__buenos_aires=Licenciatura%20en%20Ciencia%20de%20Datos&carrerade_grado__rosario=Licenciatura%20en%20Ciencia%20de%20Datos"
        url_state=True
    elif query['id_question'] == 8 or query['id_question'] == 9 or query['id_question'] == 10 or query['id_question'] == 11:
        url = "https://uca.edu.ar/es/noticias/inauguracion-del-laboratorio-de-ciencia-de-datos-e-inteligencia-artificial-1"
        url_state=True
    else:
        url_state=False
        url=""
    return [url_state, url] if url_state else [url_state]


def Question(id_question, cursor):
    cursor.execute("Select * from Question;")
    questions = cursor.fetchall()

    flag = False
    i=0
    while flag == False and i < len(questions):
        if questions[i][0] == id_question:
            question = questions[i][2]
            answer = questions[i][3]
            flag = True
        else:
            i+=1

    query = {"question": question, "answer": answer, "id_question": id_question}
    return query

# Función principal para la aplicación web
def main():
    
    hide_menu_style = """
    <style>
    header {visibility: hidden; }
    </style>
    """
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"]{
    background-image: url("");
    background-size: cover;
    }
    </style>
    """

    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.title("🤖 ChatBot + LLM sobre la Licenciatura en Ciencia de Datos")
    st.markdown("Este chatbot está diseñado para brindar información sobre la Licenciatura en Ciencia de Datos. Las respuestas son generados con Inteligencia Artificial, por lo que si no son coherentes te recomendamos que vuelvas a preguntar. Antes de empezar te pido que ingreses algunos datos para que la respuesta sea personalizada segun tus preferencias y conocimiento.")

    host = 'chatbotdb.c9iy624owubo.us-east-1.rds.amazonaws.com'
    port = 3306
    user = 'admin'
    password = 'chatbotUCA2024'
    database = 'chatbotdb'

    try:
        connection = pymysql.connect(host=host, port=port , user= user, passwd = password, db= database)

    except:
        print("Error de conexion")


    # Interacción inicial para obtener información del usuario
    with st.chat_message(name="assistant", avatar = "https://i.ibb.co/hBymPw0/image-removebg-preview.png"):
        memory = {}
        name = st.text_input("Cuál es tu nombre?")
        memory['name'] = name
    
    with st.chat_message(name="assistant",avatar="https://i.ibb.co/hBymPw0/image-removebg-preview.png"):
    # Crear un formulario para agrupar los widgets de selección
        with st.form(key="form"):
        # Agregar la opción "Seleccione opción" a cada lista de opciones
            education_options = ["Seleccione opción", "🎓 Educación secundaria", "🎓 Licenciatura / Grado universitario", "🎓 Postgrado / Maestría / Doctorado"]
            education = st.selectbox("🎓 ¿Cuál es tu nivel de educación más alto alcanzado hasta ahora?", education_options)
            memory['education'] = education[2:]

            grade_options = ["Seleccione opción", "⚪️ Principiante (sin experiencia previa)", "🟡 Intermedio (alguna experiencia, pero limitada)", "🟠 Avanzado (amplia experiencia)"]
            grade = st.selectbox("💻 ¿Cuál es tu nivel de experiencia en el campo de la carrera que estás explorando?", grade_options)
            memory['grade'] = grade[2:]

            token_temperature_options = ["Seleccione opción", "🔵 Más concisas", "⚪️ Equilibrado", "🔴 Más creativas"]
            token_temperature = st.selectbox("✏️ Elige estilo de respuesta.", token_temperature_options)

            token = 350
            temperature = 0.9

            if token_temperature == "🔵 Más concisas":
                token = 250
                temperature = 0.4
            elif token_temperature == "⚪️ Equilibrado":
                token = 300
                temperature = 0.9
            elif token_temperature == "🔴 Más creativas":
                token = 350
                temperature = 1.3

            memory['token'] = token
            memory['temperature'] = temperature


            state_options = ["Seleccione opción", "😃 Divertida", "🙂 Normal", "😐 Seria"]
            state = st.selectbox("😃 ¿Como quieres que sea la conversacion?", state_options)
            memory['state'] = state[2:]

            query_option = st.selectbox("🤔 Elige una consulta.",
                                    ["Seleccione opción",
                                     "🤔 ¿Cuánto vale la mensualidad?",
                                     "🤖 ¿De qué trata la carrera de la Licenciatura en Ciencia de Datos?",
                                     "📄 ¿Cuál es el plan de estudio y la duración de la carrera?",
                                     "💼 ¿Cuáles son las aplicaciones laborales?",
                                     "🏢 Información Laboratorio de Ciencia de Datos",
                                     "💻 ¿Que habilidades se desarrollan en la carreras?"])
            
            sub_questions = {
                "Seleccione opción": "",
                "🤔 ¿Cuánto vale la mensualidad?": "",
                "🤖 ¿De qué trata la carrera de la Licenciatura en Ciencia de Datos?": "",
                "📄 ¿Cuál es el plan de estudio y la duración de la carrera?": "",
                "💼 ¿Cuáles son las aplicaciones laborales?": ["Seleccione sector", "🚑 Sector Médico", "💹 Sector Económico", "🎨 Sector Artístico", "🏢 Sector Empresarial"],
                "🏢 Información Laboratorio de Ciencia de Datos": ["Seleccione opción","🤔 ¿Que es el laboratorio de ciencia de datos?", "🔍 ¿Qué puedo encontrar en el laboratorio?", "📄 ¿Cuáles son las normas de convivencia?", "👥 ¿Quienes estan a cargo del laboratorio?"],
                "💻 ¿Que habilidades se desarrollan en la carreras?": ""
            }

            subquery_option = st.selectbox("Algunas preguntas tienen sub-preguntas", sub_questions[query_option])

        # Crear un botón de envío para el formulario
            submitted = st.form_submit_button("Hacer consulta")

    # Si el botón se presiona, verificar si todas las opciones son válidas
        if submitted:
        # Crear una variable booleana para indicar si el usuario ha completado todas las opciones
            completed = True

        # Si alguna opción es "Seleccione opción", cambiar el valor de la variable a False y mostrar un mensaje de error
            if name == "":
                completed = False
                st.error("Por favor, escribe tu nombre.")
            if education == "Seleccione opción":
                completed = False
                st.error("Por favor, elige tu nivel de educación.")
            if grade == "Seleccione opción":
                completed = False
                st.error("Por favor, elige tu nivel de experiencia.")
            if token == "Seleccione opción":
                completed = False
                st.error("Por favor, elige el estilo de respuesta.")
            if state == "Seleccione opción":
                completed = False
                st.error("Por favor, elige el tono de la conversación.")
            if query_option == "Seleccione opción":
                completed = False
                st.error("Por favor, elige una consulta válida.")

        # Si todas las opciones son válidas, procesar la consulta normalmente
            if completed:
                query = {}
                flag = True

                cursor = connection.cursor()

                if query_option == "🤔 ¿Cuánto vale la mensualidad?":
                    id_question = 1
                    query = Question(id_question, cursor)
                
                elif query_option == "🤖 ¿De qué trata la carrera de la Licenciatura en Ciencia de Datos?":
                    id_question = 2
                    query = Question(id_question, cursor)
                
                elif query_option == "📄 ¿Cuál es el plan de estudio y la duración de la carrera?":
                    id_question = 3
                    query = Question(id_question, cursor)
                
                elif query_option == "💼 ¿Cuáles son las aplicaciones laborales?" and subquery_option == "🚑 Sector Médico":
                    id_question = 4
                    query = Question(id_question, cursor)
                
                elif query_option == "💼 ¿Cuáles son las aplicaciones laborales?" and subquery_option ==  "💹 Sector Económico":
                    id_question = 5
                    query = Question(id_question, cursor)
                    
                elif query_option == "💼 ¿Cuáles son las aplicaciones laborales?" and subquery_option ==  "🎨 Sector Artístico":
                    id_question = 6
                    query = Question(id_question, cursor)
                    
                elif query_option == "💼 ¿Cuáles son las aplicaciones laborales?" and subquery_option ==  "🏢 Sector Empresarial":
                    id_question = 7
                    query = Question(id_question, cursor)
                
                elif query_option == "🏢 Información Laboratorio de Ciencia de Datos" and subquery_option == "🤔 ¿Que es el laboratorio de ciencia de datos?":
                    id_question = 8
                    query = Question(id_question, cursor)

                elif query_option ==  "🏢 Información Laboratorio de Ciencia de Datos" and subquery_option == "🔍 ¿Qué puedo encontrar en el laboratorio?":
                    id_question = 9
                    query = Question(id_question, cursor)

                elif query_option ==  "🏢 Información Laboratorio de Ciencia de Datos" and subquery_option == "📄 ¿Cuáles son las normas de convivencia?":
                    id_question = 10
                    query = Question(id_question, cursor)

                elif query_option ==  "🏢 Información Laboratorio de Ciencia de Datos" and subquery_option == "👥 ¿Quienes estan a cargo del laboratorio?":
                    id_question = 11
                    query = Question(id_question, cursor)
                
                elif query_option == "💻 ¿Que habilidades se desarrollan en la carreras?":
                    id_question = 12
                    query = Question(id_question, cursor)

                else: # Si el usuario elige "Seleccione sector"
                    flag = False
                    if 'query_prev' not in st.session_state:
                        st.session_state['query_prev'] = ""
                    if 'contador' not in st.session_state:
                        st.session_state['contador'] = 0
                    if query_option != st.session_state['query_prev']:
                        st.session_state['contador'] = 0
                    if submitted:
                        st.session_state['contador'] += 1
                    if st.session_state['contador'] > 1:
                        st.error("Por favor, elige una consulta válida.")
                        del st.session_state['contador']
                st.session_state['query_prev'] = query_option

                if 'first_interaction' not in st.session_state:
                    st.session_state['first_interaction'] = True
        
            # Llamar a la función chatbot_interaction con el valor del session state
                if flag:
                    response = chatbot_interaction(memory, query, st.session_state['first_interaction'])
        
        # Actualizar el valor del session state a False
                    st.session_state['first_interaction'] = False
                
                    image_html = """
                    <img src="https://i.ibb.co/hBymPw0/image-removebg-preview.png" style="width:50px; height:50px; margin-left:-14px">
                    """

                # Crear el contenedor con el título y la imagen
                    container_html = f"""
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    {image_html}
                    <h1 style="text-align: left; font-size: 22px; vertical-align: middle; font-weight: bold; margin-left: 1px; color: black; ">L.U.C.A</h1>
                    </div>
                    """

    # Mostrar el contenedor usando la función st.components.v1.html
                    st.components.v1.html(container_html, height=100)
                    url_info=links(query)
                    if url_info[0]==True: 
                        response+= f"\nSi tienes alguna consulta más sobre este tema, podes hacer clic en el botón de abajo."
                #'ChatBot-AI-main\L.U.C.A.jpg'
                    text = "" # Inicializar el texto vacío
                    placeholder = st.empty() # Crear un marcador de posición vacío
                    for char in response:
                        text += char # Agregar el carácter actual al texto
                        placeholder.markdown(f"<p style=\"margin-top:-60px;\">{text}</p>", unsafe_allow_html=True) # Escribir el texto actual en el marcador de posición
                        time.sleep(0.01) # Esperar 0.01 segundos
                    placeholder.markdown(f"<p style=\"margin-top:-60px;\">{response}</p>", unsafe_allow_html=True) # Escribir el texto completo en el marcador de posición
                    if url_info[0]==True:
                        url=url_info[1]
                        st.link_button("Ir a la página web", url=url)
                        #Si tienes alguna consulta más sobre este tema, podes hacer clic en el botón de abajo.


    with st.chat_message(name="assistant", avatar = "https://i.ibb.co/hBymPw0/image-removebg-preview.png"):
        with st.form(key="form2"):
            st.write("Para enviar su calificación complete al menos un campo.")
            star_option = st.selectbox("⭐️ Califica al ChatBot del 1 al 5", ["Seleccione opción","⭐️ 1","⭐️ 2","⭐️ 3","⭐️ 4","⭐️ 5"])
            new_question = st.text_input("✏️ ¿Qué pregunta te gustaria añadir?")

            submitted_2 = st.form_submit_button("Enviar")

        if submitted_2:
            completed_2 = True

            if star_option == "Seleccione opción":
                completed_2 = False
                st.error("Por favor, rellene al menos un campo.")
        
            if completed_2:
                insert = connection.cursor()

                if star_option == "⭐️ 1":
                    star = 1
                elif star_option == "⭐️ 2":
                    star = 2
                elif star_option == "⭐️ 3":
                    star = 3
                elif star_option == "⭐️ 4":
                    star = 4
                elif star_option == "⭐️ 5":
                    star = 5

                if new_question == "":
                    new_question = None

                review = {"star": star, "new_question": new_question}

                if new_question == None:
                    query_insert = f"INSERT INTO Review(name, star, new_question) VALUES ('{memory['name']}', {review['star']}, NULL)"
                else:
                    query_insert = f"INSERT INTO Review(name, star, new_question) VALUES ('{memory['name']}', {review['star']}, '{review['new_question']}')"
                
                insert.execute(query_insert)
                connection.commit()
                insert.close()

                st.success("Enviado con éxito")


    connection.close()

main()
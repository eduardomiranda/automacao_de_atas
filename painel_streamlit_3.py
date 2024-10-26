from moviepy.editor import AudioFileClip
import uuid

import streamlit as st
import assemblyai as aai
from openai import OpenAI


aai.settings.api_key = st.secrets['assemblyai']['api_key']
client = OpenAI(api_key= st.secrets['openai']['api_key'])






def mp4_to_mp3(mp4_filename, mp3_filename):

	arquivo_a_ser_convertido = AudioFileClip(mp4_filename)
	arquivo_a_ser_convertido.write_audiofile(mp3_filename)
	arquivo_a_ser_convertido.close()




def generate_response(prompt_system, prompt_text):

	response = client.chat.completions.create(
		model="gpt-4o-2024-08-06",  # Specify the model to use
		messages=[
			{"role": "system", "content": prompt_system},
			{"role": "user", "content": prompt_text}
		],
		# max_tokens=150,			# Limits how long the response can be
		temperature=0.7			# A value between 0-1 that controls randomness
	)  # Ensure this line ends with the closing parenthesis


	texto_retorno = response.choices[0].message.content.strip()

	return texto_retorno






st.title('Automação de atas')

st.write('Criando uma ferramenta de automação de atas de reunião com tecnologia de IA com Python')


uploaded_file = st.file_uploader("Selecione o seu arquivo", accept_multiple_files=False, type = ['mp4'])

if uploaded_file:

	with st.spinner('Convertendo de mp4 para mp3'):
	
		mp4_filename = uploaded_file.name
		mp3_filename = '{nome_arquivo}.mp3'.format(nome_arquivo = uuid.uuid4().hex)

		tempfile = open(mp4_filename, 'wb')
		tempfile.write(uploaded_file.read())

		mp4_to_mp3(mp4_filename, mp3_filename)

	st.success("Conversão de MP4 para MP3 realizada!")



	with st.spinner('Convertendo de mp3 para texto'):

		transcriber = aai.Transcriber()

		config = aai.TranscriptionConfig( speaker_labels = True, speakers_expected = 2, language_code = 'pt' )

		transcriber = aai.Transcriber()
		transcricao = transcriber.transcribe(mp3_filename, config = config)


		texto_transcrito = ''
		for sentenca in transcricao.utterances:
			texto_transcrito += f"Pessoa {sentenca.speaker}: {sentenca.text}"
			texto_transcrito += '\n'

		st.text_area('Transcrição', texto_transcrito)

	st.success("Transcrição realizada!")



	with st.spinner('Gernado ata de reunião'):

		prompt_system = 'Você é um ótimo gerente de projetos com grandes capacidades de criação de atas de reunião'
		
		prompt_text = 'Em uma redação de nível especializado, resuma as notas da reunião em um único parágrafo. Em seguida, escreva uma lista de cada um de seus pontos-chaves tratados na reunião. Por fim, liste as próximas etapas ou itens de ação sugeridos pelos palestrantes, se houver.'
		
		prompt_text += '==========='
		prompt_text += texto_transcrito

		texto_retorno = generate_response(prompt_system, prompt_text)

		st.markdown(texto_retorno)



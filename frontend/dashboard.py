from h2o_wave import main, app, Q, ui
from h2o_wave import data as da
from .chatbot import *
import os
import os.path
import asyncio
import requests
import json

prev_messages = [{'content': f'Message {i}', 'from_user': i % 2 == 0} for i in range(100)]
radar_data = []
LOAD_SIZE = 10
n_top_candidates = 4

@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        q.page['meta'] = ui.meta_card(box='', layouts=[
            ui.layout(
                breakpoint='m',
                #width='1200px',

                # Create zones for each divisions
                zones=[ # 76, 105, 780
                    ui.zone('header', size='5%'),
                    ui.zone('filters', direction=ui.ZoneDirection.ROW, size='7%'),
                    ui.zone('middle', direction=ui.ZoneDirection.ROW, size='85%',
                            zones=[ui.zone('middle_left',size='35%', direction=ui.ZoneDirection.COLUMN,
                                        zones=[ui.zone('ltop', size='10%'),
                                                ui.zone('lbottom', size='79%')]),
                                ui.zone('middle_right', size='65%',direction=ui.ZoneDirection.COLUMN, 
                                        zones=[ui.zone('rtop'),
                                                ui.zone('rmid', align = 'center', justify ='between', direction = ui.ZoneDirection.ROW),
                                                ui.zone('rbottom')])]),
                    ui.zone('footer', size='80px')]),
                    ],
            themes=[
                ui.theme(
                    name='dsa4213',
                    primary='#20283d',
                    text='#470324',
                    card='#fffffa',
                    page='#e8e6e6',
                    )
                    ],
            theme='dsa4213'

    )
        
        q.page['header'] = ui.header_card(box='header', title='Resume Analysis', subtitle='DSA4213 Group Whisper',
                                        image='https://wave.h2o.ai/img/h2o-logo.svg')
        
        
        ### Create filters ###
        q.page['filter1'] = ui.form_card(
            box='filters',
            items=[
                ui.dropdown(name='open_positions', label='Open Positions', choices=[
                    ui.choice(name='Position 1', label='Backend Engineer'),
                    ui.choice(name='position_2', label='Frontend Engineer'),
                    ui.choice(name='position_3', label='Data Scientist')

        ])])
        q.page['filter2'] = ui.form_card(
            box='filters',
            items=[
                ui.dropdown(name='region', label='Region', choices=[
                    ui.choice(name='region_1', label='ASEAN'),
                    ui.choice(name='region_2', label='Greater China'),
                    ui.choice(name='region_3', label='Japan')
        ])])
        q.page['filter3'] = ui.form_card(
            box='filters',
            items=[
                ui.dropdown(name='department', label='Department', choices=[
                    ui.choice(name='department_1', label='Technology'),
                    ui.choice(name='department_2', label='Risk'),
                    ui.choice(name='department_3', label='Finance')
        ])])

        # q.page['text1'] = ui.form_card(
        #     box='filters',
        #     items=[
        #         ui.message_bar(type='success', text=q.args.open_positions)
        #     ]
        # )
        ################ 

        # Create KPI Card
        q.page['kpi'] = ui.form_card(box=ui.box('ltop'), items=[
            ui.stats(inset=True, justify='between',items=[
                ui.stat(label='',value='70', caption='Current'),
                ui.stat(label='',value='+2', caption='vs YSTD'),
                ui.stat(label='', value='2.85%', caption='∆'),
        ])
        # todo: add color to numbers based on +/- change
    
    ])
        
        radar_data = json.loads(
            requests.get('http://localhost:4000/candidate/recommendation/radar-plot').json()
        )
        # Create table title:
        q.page['tb_title'] = ui.form_card(
            box= ui.box(zone='rtop', size='0'),
            items=[
                ui.text_l(f'| Top {min(len(radar_data),4)} Candidate Recommendation'),
            ],
        )

        # Create Radar plots
        
        print(radar_data)

        for i in range(1, min(len(radar_data)+1,n_top_candidates+1)):
            print(i)
            q.page[f"top{i}Radar"] = ui.plot_card(
                box = ui.box('rmid'),
                title = f"Candidate {i}",
                data = da('Metrics Score', 5, rows=[
                    ('API design experience', radar_data[i-1]['apiDesignExperience']),
                    ('Framework knowledge', radar_data[i-1]['frameworkKnowledge']),
                    ('Databases skill', radar_data[i-1]['databaseSkill']),
                    ('Cybersecurity knowledge', radar_data[i-1]['cybersecurityKnowledge']),
                    ('App dev experience', radar_data[i-1]['appDevExperience']),
                ]),
                plot=ui.plot([
                ui.mark(
                        coord='polar',
                        type='interval',
                        x='=Metrics',
                        y='=Score',
                        color='=Metrics',
                        stack='auto',
                        y_min=0,
                        stroke_color='$card'
                    )
                ]),
            )

        # Table content
        ## NOTE: only modify this to add columns. 
        ## key is UI column name, value is db column name
        labels = {
            'Name' : "candidate_name",
            'Experience Level(Yr)' : 'candidate_experience',
            'Education' : 'candidate_education',
            'Strength' : 'candidate_strength',
            'Most Rec Job' : 'candidate_MostRecenJobTitle',
            'Unemployed Duration(M)' : 'last_employed',
        }
        data = json.loads(
            requests.get('http://localhost:4000/candidate/recommendation/table').json()
        )

        q.page['table'] = ui.form_card(box='rbottom', items=[
        ui.table(
            name='table',
            columns=[ui.table_column(name=n, label=l, filterable=True) for l, n in labels.items()],
            rows=[ui.table_row(name=f'row{i}', cells=[str(row[label]) for label in labels.values()]) for i, row in enumerate(data)],
            downloadable=True,
        )
    ])
        
        # Create Pie Chart (Experience Level Distribution)
        ex_data = json.loads(
            requests.get('http://localhost:4000/candidate/experience-levels').json()
        )
        junior = 0
        mideum = 0
        senior = 0
        for ex in ex_data:
            year = ex['candidate_experience']
            count = ex['count']

            if year <= 3:
                junior += count
            elif year <=6:
                mideum += count
            else:
                senior += count
        total = junior + mideum + senior
        
        j_rate = float(junior/total)
        m_rate = float(mideum/total)
        s_rate = float(senior/total)
        
        print(j_rate, m_rate, s_rate)

        q.page['exp_dits'] = ui.wide_pie_stat_card(box='lbottom', title='Experience Level Distribution', pies=[
            ui.pie(label='0-3 years', value=f'{j_rate*100}%', fraction=j_rate, color='blue'),
            ui.pie(label='3-6 years', value=f'{m_rate*100}%', fraction=m_rate, color='pink'),
            ui.pie(label='>6 years', value=f'{s_rate*100}%', fraction=s_rate, color='salmon'),
    ])
        # Upload button
        q.page['Upload'] = ui.form_card(box='lbottom', items=[
            ui.text_xl('Upload candidate resume files here'),
            ui.file_upload(name='user_files', label='Upload', multiple=True, file_extensions=['pdf']),
        ])

        ### Chat Bot ###
        q.client.current_load_page = len(prev_messages)
        q.page['chat_bot'] = ui.chatbot_card(
            box='rbottom',
            name='chatbot', 
            data=da(fields='content from_user', t='list', rows=[
                    ['Hello', True],
                    ['Hi', False],
                    ['Hello', True],
                    ['Hi', False],
                    ['Hello', True],
                    ['Hi', False],
                    ['Hello', True],
                    ['Hi', False],
            ]),
            events=['scroll_up'],
            placeholder='Ask me anything...',
            )   
        ################
        
        # Download link or results
        download_path = "" #await q.site.upload(['results.csv'])
        q.page['download'] = ui.form_card(box='lbottom', items = [
            ui.link(label='Download Results', path=download_path, download=True),
        ])
        q.client.initialized = True

    else:
        ### Filters #### 
        if q.args.chatbot: # TODO: get frontend extraction of filters working
            # FOR NOW WE SIMULATE NEW DATA
            for i in range(1, n_top_candidates+1): # removal of existing radar plots
                del q.page[''.join(['top', str(i), 'Radar'])]

            # TODO: extract data for new radar plots
            for i in range(1, n_top_candidates+1): # plot new radar plots
                q.page[''.join(['top', str(i), 'Radar'])] = ui.plot_card(
                    box = ui.box('rmid'),
                    title = ''.join(['Candidate', str(i)]),
                    data = da('Metrics Score', 6, rows=[
                        ('API design experience', 1),
                        ('Framework knowledge', 1),
                        ('Databases skill', 1),
                        ('Cybersecurity knowledge', 1),
                        ('App dev experience', 3),
                    ]),
                    plot=ui.plot([
                    ui.mark(
                            coord='polar',
                            type='interval',
                            x='=Metrics',
                            y='=Score',
                            color='=Metrics',
                            stack='auto',
                            y_min=0,
                            stroke_color='$card'
                        )
                    ]),
                )
        ################

        ### File Upload ###
        if q.args.user_files:
            links = q.args.user_files 
            items = [ui.text_xl('Files uploaded!')]
            for link in links:
                local_path = await q.site.download(link, '.')
                #
                # The file is now available locally; process the file.
                # To keep this example simple, we just read the file size.
                #
                size = os.path.getsize(local_path)

                with open(local_path, 'rb') as file:
                    files = {
                        'file': (local_path, file),
                    }

                    response = requests.post('http://localhost:4000/file/upload', files=files)
                print(response.text)


                items.append(ui.link(label=f'{os.path.basename(link)} ({size} bytes)', download=True, path=link))
                # Clean up
                os.remove(local_path)

            items.append(ui.button(name='back', label='Back', primary=True))
            q.page['Upload'].items = items

        ################

        ### Chat Bot ### 
        # New message
        if q.args.chatbot:
            # If user message:
            q.page['chat_bot'].data += [q.args.chatbot, True]
            # If bot message:
            q.page['chat_bot'].data += ['', False]
            
            # Stream bot response.
            q.client.task = asyncio.create_task(stream_chatbot_response(q.args.chatbot, q))
        
        # User scroll up to see chat history
        if q.events.chatbot and q.events.chatbot.scroll_up:
            if q.client.current_load_page == 0:
                # If we reached the end, signal it to Wave by setting prev_items to empty list.
                q.page['chat_bot'].prev_items = []
            else:
                end = q.client.current_load_page - LOAD_SIZE
                q.page['chat_bot'].prev_items = prev_messages[end:q.client.current_load_page]
                q.client.current_load_page = end
                await q.sleep(0.5)  # Simulate network latency.

        ################
    await q.page.save()
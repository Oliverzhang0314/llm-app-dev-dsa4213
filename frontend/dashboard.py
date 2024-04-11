from h2o_wave import main, app, Q, ui
from h2o_wave import data as da
from chatbot import *
import os
import os.path
import asyncio

prev_messages = [{'content': f'Message {i}', 'from_user': i % 2 == 0} for i in range(100)]
LOAD_SIZE = 10

@app('/')
async def serve(q: Q):
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
                                              ui.zone('lbottom', size='60%')]),
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
        box=ui.box('filters'),
        items=[
            ui.dropdown(name='open_positions', label='Open Positions', choices=[
                ui.choice(name='position_1', label='Position 1'),
                ui.choice(name='position_2', label='Position 2'),
                ui.choice(name='position_3', label='Position 3')

    ])])
    q.page['filter2'] = ui.form_card(
        box='filters',
        items=[
            ui.dropdown(name='region', label='Region', choices=[
                ui.choice(name='region_1', label='Region 1'),
                ui.choice(name='region_2', label='Region 2'),
                ui.choice(name='region_3', label='Region 3')
    ])])
    q.page['filter3'] = ui.form_card(
        box='filters',
        items=[
            ui.dropdown(name='department', label='Department', choices=[
                ui.choice(name='department_1', label='Department 1'),
                ui.choice(name='department_2', label='Department 2'),
                ui.choice(name='department_3', label='Department 3')
    ])])
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
    
    # Re-create table title:

    q.page['tb_title'] = ui.form_card(
        box= ui.box(zone='rtop', size='0'),
        items=[
            ui.text_l('| Top 4 Candidate Recommendation'),
        ],
    )
    
    # Create table title
    #q.page['tb_title'] = ui.header_card(box=('rtop'), subtitle='', title='| Top 4 Candidate Recommendation', color='card')

    q.page['top1Radar'] = ui.plot_card(
        box = ui.box('rmid'),
        title ='Radar Plot',
        data = da('Metrics Score', 6, rows=[
            ('Work Attitude', 8),
            ('Adaptability', 9),
            ('Collaboration', 9),
            ('Communication', 8),
            ('Work Ethics', 9.3),
            ('Leadership', 9.3),
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

    q.page['top2Radar'] = ui.plot_card(
        box = ui.box('rmid'),
        title ='Candidate2',
        data = da('Metrics Score', 6, rows=[
            ('Work Attitude', 7),
            ('Adaptability', 9),
            ('Collaboration', 6.8),
            ('Communication', 7),
            ('Work Ethics', 9),
            ('Leadership', 5),
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

    q.page['top3Radar'] = ui.plot_card(
        box = ui.box('rmid'),
        title ='Candidate3',
        data = da('Metrics Score', 6, rows=[
            ('Work Attitude', 6),
            ('Adaptability', 6),
            ('Collaboration', 5),
            ('Communication', 4),
            ('Work Ethics', 9.3),
            ('Leadership', 6),
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

    q.page['top4Radar'] = ui.plot_card(
        box = ui.box('rmid'),
        title ='Candidate4',
        data = da('Metrics Score', 6, rows=[
            ('Work Attitude', 6),
            ('Adaptability', 6),
            ('Collaboration', 5),
            ('Communication', 4),
            ('Work Ethics', 7),
            ('Leadership', 6),
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
    names = ['name','exp','education','strength','rjt','trjt','resume']
    labels = ['Name','Experience Level(Yr)','Education','Strength','Most Rec Job','Unemployed Duration(M)','Resume']
    data = []

    q.page['table'] = ui.form_card(box='rbottom', items=[
    ui.table(
        name='table',
        columns=[
            ui.table_column(name=names[0], label=labels[0]),
            ui.table_column(name=names[1], label=labels[1], filterable=True),
            ui.table_column(name=names[2], label=labels[2], filterable=True),
            ui.table_column(name=names[3], label=labels[3], filterable=True),
            ui.table_column(name=names[4], label=labels[4], filterable=True),
            ui.table_column(name=names[5], label=labels[5], filterable=True),
            ui.table_column(name=names[6], label=labels[6], filterable=True)
            ],
        rows=[
            ui.table_row(name='row1', cells=['John','1']),
            ui.table_row(name='row2', cells=['Alice','0.5']),
            ui.table_row(name='row3', cells=['Bob','2']),
            ui.table_row(name='row4', cells=['John','1']),
            ui.table_row(name='row5', cells=['Alice','2']),
            ui.table_row(name='row6', cells=['Bob','2']),
            ui.table_row(name='row7', cells=['John','1']),
            ui.table_row(name='row8', cells=['Alice','1']),
        ],
    )
])
    
    # Create Pie Chart (Experience Level Distribution)
    q.page['exp_dits'] = ui.wide_pie_stat_card(box='lbottom', title='Experience Level Distribution', pies=[
        ui.pie(label='0-1 years', value='65%', fraction=0.65, color='blue'),
        ui.pie(label='2-4 years', value='25%', fraction=0.25, color='pink'),
        ui.pie(label='>4 years', value='10%', fraction=0.10, color='salmon'),
])
    # Upload button
    links = q.args.user_files
    if links:
        items = [ui.text_xl('Files uploaded!')]
        for link in links:
            local_path = await q.site.download(link, '.')
            #
            # The file is now available locally; process the file.
            # To keep this example simple, we just read the file size.
            #
            size = os.path.getsize(local_path)

            items.append(ui.link(label=f'{os.path.basename(link)} ({size} bytes)', download=True, path=link))
            # Clean up
            os.remove(local_path)

        items.append(ui.button(name='back', label='Back', primary=True))
        q.page['Upload'].items = items
    else:
        q.page['Upload'] = ui.form_card(box='lbottom', items=[
            ui.text_xl('Upload candidate resume files here'),
            ui.file_upload(name='user_files', label='Upload', multiple=True),
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

    # New message
    if q.args.chatbot:
        # If user message:
        q.page['chat_bot'].data += [q.args.chatbot, True]
        # If bot message:
        q.page['chat_bot'].data += ['', False]
        
        # Stream bot response.
        q.client.task = asyncio.create_task(stream_chatbot_response(q.args.chatbot, q))
        await q.page.save()
    
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
    
    # Download link or results
    download_path = "" #await q.site.upload(['results.csv'])
    q.page['download'] = ui.form_card(box='lbottom', items = [
        ui.link(label='Download Results', path=download_path, download=True),
    ])
    await q.page.save()


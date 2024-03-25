from h2o_wave import main, app, Q, ui
from h2o_wave import data as da

@app('/')
async def serve(q: Q):
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xs',
            #width='1200px',

            # Create zones for each divisions
            zones=[
                ui.zone('header', size='76px'),
                ui.zone('filters', direction=ui.ZoneDirection.ROW, size='105px'),
                ui.zone('middle', direction=ui.ZoneDirection.ROW, size='780px', justify='around',
                        zones=[ui.zone('middle_left',direction=ui.ZoneDirection.COLUMN, 
                                       zones=[ui.zone('ltop', size='40%'),
                                              ui.zone('lbottom', size='40%')]),
                               ui.zone('middle_right', size='75%',justify='between',direction=ui.ZoneDirection.COLUMN, 
                                       zones=[ui.zone('rtop'),
                                              ui.zone('rmid', size = '45%', justify ='between', direction = ui.ZoneDirection.ROW),
                                              ui.zone('rbottom', size='50%')])]),
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
    
    '''
    q.page['title'] = ui.section_card(
        box='title',
        title='Resume Analysis',
        subtitle='Subtitle',
        items=[
            ui.toggle(name='search', label='sample term', value=True),
            ui.dropdown(name='distribution', label='', value='option0', choices=[
                ui.choice(name=f'option{i}', label='sample term') for i in range(5)
            ]),
            ui.date_picker(name='target_date', label='', value='2020-12-25'),
        ])
    '''
    
    # Create filters
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


    # Create KPI Card
    q.page['kpi'] = ui.form_card(box=ui.box('ltop'), items=[
        ui.stats(inset=True, justify='between',items=[
            ui.stat(label='',value='70', caption='Current'),
            ui.stat(label='',value='+2', caption='vs YSTD'),
            ui.stat(label='', value='2.85%', caption='∆'),
        ])
    # todo: add color to numbers based on +/- change
 
    ])
    
    # Create table title
    q.page['tb_title'] = ui.header_card(box=('rtop'), subtitle='', title='| Top 4 Candidate Recommendation', color='card')
    # Create Top Candidates Radar Plots for Strength Comnparison

    q.page['top1Radar'] = ui.plot_card(
        box = ui.box('rmid', order = 1, size = 10),
        title ='Radar Plot',
        data = da('Metrics Score', 6, rows=[
            ('Work Attitude', 8),
            ('Attendance', 9),
            ('Collaboration', 9),
            ('Communication', 8),
            ('Competitiveness', 9.3),
            ('Technical Skills', 9.3),
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
        box = ui.box('rmid', order = 2, size = 10),
        title ='Candidate2',
        data = da('Metrics Score', 6, rows=[
            ('Work Attitude', 7),
            ('Attendance', 9),
            ('Collaboration', 8),
            ('Communication', 8),
            ('Competitiveness', 7.5),
            ('Technical Skills', 6.3),
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
        box = ui.box('rmid', order = 3, size = 10),
        title ='Candidate3',
        data = da('Metrics Score', 6, rows=[
            ('Work Attitude', 7),
            ('Attendance', 8),
            ('Collaboration', 7),
            ('Communication', 6),
            ('Competitiveness', 7.5),
            ('Technical Skills', 7),
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
            ui.table_column(name=names[2], label=labels[2]),
            ui.table_column(name=names[3], label=labels[3]),
            ui.table_column(name=names[4], label=labels[4]),
            ui.table_column(name=names[5], label=labels[5]),
            ui.table_column(name=names[6], label=labels[6])
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
    await q.page.save()


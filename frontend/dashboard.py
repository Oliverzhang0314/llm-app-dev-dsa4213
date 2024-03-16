from h2o_wave import main, app, Q, ui

@app('/')
async def serve(q: Q):
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xs',
            width='1300px',

            # Create zones for each divisions
            zones=[
                ui.zone('header', size='76px'),
                ui.zone('filters', direction=ui.ZoneDirection.ROW, size='95px', align='center', justify='around'),
                ui.zone('middle', direction=ui.ZoneDirection.ROW, size='780px', justify='around', 
                        zones=[ui.zone('middle_left'),
                               ui.zone('middle_right', size='70%',justify='between',direction=ui.ZoneDirection.COLUMN, 
                                       zones=[ui.zone('rtop'),
                                              ui.zone('rbottom')])]),
                ui.zone('footer', size='80px')])
                ])
    
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
        box='filters',
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
    q.page['kpi'] = ui.form_card(box='middle_left',items=[
    ui.stats(inset=True, justify='between', items=[
        ui.stat(label='',value='70', caption='Current'),
        ui.stat(label='',value='+2', caption='vs YSTD'),
        ui.stat(label='', value='2.85%', caption='∆'),
    ])
])
    # Create table title
    q.page['tb_title'] = ui.header_card(box=('rtop'), subtitle='', title='Top 4 Candidate Recommendation', color='card')

    # Create table
    
    await q.page.save()


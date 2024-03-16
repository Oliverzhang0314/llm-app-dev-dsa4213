from h2o_wave import main, app, Q, ui



@app('/')
async def serve(q: Q):
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xs',
            width='1300px',
            zones=[
                ui.zone('header', size='76px'),
                ui.zone('filters', direction=ui.ZoneDirection.ROW, size='95px',
                        align='center', justify='around'),

                ui.zone('middle', direction=ui.ZoneDirection.ROW, size='385px'),
                ui.zone('bottom', direction=ui.ZoneDirection.ROW, size='385px', zones=[
                    ui.zone('bottom_left'),
                    ui.zone('bottom_right', size='66%'),
                ]),
                ui.zone('footer', size='80px'),
            ]
        )
    ])
    
    q.page['header'] = ui.header_card(box='header', title='Resume Analysis', subtitle='dsa4213-group-project',
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

    await q.page.save()


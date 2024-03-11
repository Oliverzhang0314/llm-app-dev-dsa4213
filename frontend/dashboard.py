from h2o_wave import main, app, Q, ui



@app('/')
async def serve(q: Q):
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xs',
            width='1200px',
            zones=[
                ui.zone('header', size='76px'),
                ui.zone('title'),
                ui.zone('top', direction=ui.ZoneDirection.ROW, size='385px', zones=[
                    ui.zone('top_left'),
                    ui.zone('top_right', zones=[
                        ui.zone('top_right_top', direction=ui.ZoneDirection.ROW, size='1'),
                        ui.zone('top_right_bottom', size='1'),
                    ]),
                ]),
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
        ],
    )


    await q.page.save()


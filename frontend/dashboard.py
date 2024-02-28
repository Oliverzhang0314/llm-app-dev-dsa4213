from h2o_wave import main, app, Q, ui

@app('/foo')
async def serve(q: Q):
    # Modify the page
    q.page['test'] = ui.ui.markdown_card(box='1 1 2 2', title='hello world', content='test')

    # Save the page
    await q.page.save()
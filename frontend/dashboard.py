from h2o_wave import main, app, Q, ui

@app('/foo')
async def serve(q: Q):
    # Modify the page
    q.page['qux'] = ui.some_card()

    # Save the page
    await q.page.save()
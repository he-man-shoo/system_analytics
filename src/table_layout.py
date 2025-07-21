import dash

def table_format(table):
    return dash.dash_table.DataTable(table.to_dict('records'), 
                                        style_data={
                                                    'color': 'black',
                                                    'backgroundColor': 'white', 
                                                    'font-family':'arial',
                                                    'font-size': '20px',
                                                    'border': '1px solid black',
                                                    'textAlign': 'left',
                                                    'padding': '10px',
                                                    },
                                        style_cell={
                                                    'whiteSpace': 'normal',
                                                    'height': 'auto',
                                                     },
                                        style_data_conditional=[
                                                                {
                                                                'if': {'row_index': 'odd'},
                                                                'backgroundColor': 'rgb(220, 207, 235)',
                                                                }, 
                                                                {
                                                                'if': {
                                                                    'column_id': 'Value'
                                                                    },
                                                                    'textAlign': 'center'
                                                                },
                                                                {
                                                                'if': {
                                                                    'column_id': 'Augmentation Number'
                                                                    },
                                                                    'textAlign': 'center'
                                                                },
                                                                {
                                                                'if': {
                                                                    'column_id': 'Augmentation Year'
                                                                    },
                                                                    'textAlign': 'center'
                                                                },
                                                                {
                                                                'if': {
                                                                    'column_id': 'Augmentation Nameplate Energy (kWh)'
                                                                    },
                                                                    'textAlign': 'center'
                                                                },
                                                                {
                                                                'if': {
                                                                    'column_id': 'Months'
                                                                    },
                                                                    'textAlign': 'center'
                                                                },
                                                                {
                                                                'if': {
                                                                    'column_id': 'Duration (weeks)'
                                                                    },
                                                                    'textAlign': 'center'
                                                                },
                                                                {
                                                                'if': {
                                                                    'column_id': 'Date'
                                                                    },
                                                                    'textAlign': 'center'
                                                                },                                                                                                                                                                      
                                                            ],

                                        style_header={
                                                    'color': 'black',
                                                    'backgroundColor': 'rgb(220, 207, 235)',                                                    
                                                    'font-family':'arial',
                                                    'font-size': '20px',
                                                    'border': '1px solid black',
                                                    'textAlign': 'left',
                                                    'padding': '10px',
                                                    })
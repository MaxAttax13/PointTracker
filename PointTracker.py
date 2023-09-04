#Point counter app, now with OOPs!

# TO DO:
# Turn History into objects, read from and write to json, and have the history tab be a chart and maybe let you sort by date or name?

import PySimpleGUI as sg
import csv
import pickle
import json
import datetime
from datetime import datetime
from datetime import timedelta

version = '1.3'
changes = False #This determines whether to prompt the user to save before exiting
window_initialized = False
today = datetime.now()
yesterday = today - timedelta(days = 1)

#Defining classes and basic actions
class Action:
    def __init__(self, name, max_points, min_points, note):
        self.name = name
        self.max_points = int(max_points)
        self.min_points = int(min_points) if min_points not in ['None', None] else None
        self.note = note if note not in ['None', None] else None
    
    def determine_value(self):
        """Determine how many points should be added/removed."""
        if self.min_points is None:
            point_value = self.max_points
            return point_value
        else:
            point_value = sg.popup_get_text(f'How many points? Must be between {self.min_points} and {self.max_points}.')
            if point_value.isdigit() and int(point_value) in range(self.min_points, self.max_points + 1):
                return int(point_value)
            else:
                sg.popup_error('Invalid point value.')
                return 0
            
    def del_object(self, list):
        """Delete a goal or reward."""
        global changes
        del_confirm = sg.popup_yes_no(f'Are you sure you want to delete \"{self.name}\"?')
        if del_confirm == 'Yes' and self in list:
            list.remove(self)
            changes = True
            create_layout()
        else:
            return
            
    def info_button(self):
        """Display info about the selected goal or reward."""
        sg.popup(f'''{self.name}:
{f'{self.min_points} - {self.max_points}' if self.min_points is not None
else f'{self.max_points}'} {'points' if self.max_points > 1 else 'point'}
{self.note}''', title = 'Info')

    def edit_obj(self):
        """Edit an existing goal or reward. Passes attributes to add_edit_obj() for editing."""
        global changes
        attributes = (self.name, self.max_points, self.min_points, self.note)
        obj_type = type(self).__name__
        obj_type = obj_type.lower()
        new_attributes = add_edit_obj(obj_type, attributes)
        if not new_attributes or new_attributes is None:
            return
        self.name, self.max_points, self.min_points, self.note = new_attributes #updates the object with the new attributes, I hope
        changes = True
        create_layout()
        return

            
class Goal(Action):
    def add_counter(self, counter):
        point_value = Action.determine_value(self)
        if point_value == 0:
            return counter
        else:
            counter += point_value
            add_history(self.name, point_value, counter)
            sg.popup_quick_message(f'Added {point_value} {"point" if point_value == 1 else "points"}.', background_color = '#20471F')
            return counter

class Reward(Action):
    def subtract_counter(self, counter):
        point_value = Action.determine_value(self)
        if point_value == 0:
            return counter
        else:
            if point_value <= counter:
                counter -= point_value
                point_value = -abs(point_value)
                add_history(self.name, point_value, counter)
                sg.popup_quick_message(f'Removed {abs(point_value)} {"point" if point_value == 1 else "points"}.', background_color = '#590409')
                return counter
            else:
                sg.popup_error('Insufficient points.')
                return counter
            
class History:
    def __init__(self, date, name, new_points, total_points):
        self.date = date
        self.name = name
        self.new_points = new_points
        self.total_points = total_points

#Loading saved counter value, history, goals, and rewards
with open('counter.pickle', 'rb') as p:
    pickle_list = pickle.load(p)
    loaded_counter, points_name = pickle_list
    counter = int(loaded_counter)
with open('History.txt') as load_history:
    read_history = csv.reader(load_history)
    history = [list(row) for row in read_history]

with open('Goals.json', 'r') as f:
    load_goals = json.load(f)
goals = []
for goal_dict in load_goals:
    goal = Goal(**goal_dict)
    goals.append(goal)

with open('Rewards.json', 'r') as f:
    load_rewards = json.load(f)
rewards = []
for reward_dict in load_rewards:
    reward = Reward(**reward_dict)
    rewards.append(reward)


def save():
    """Save all changes."""
    with open('counter.pickle', 'wb') as p:
        pickle_list = (counter, points_name)
        pickle.dump(pickle_list, p)

    with open('History.txt', 'w') as h:
        for line in history:
            if line != history[0]:
                h.writelines('\n')
            h.writelines(line)

    updated_goals = [goal.__dict__ for goal in goals] # Convert the list of Goal objects to a list of dictionaries
    with open('Goals.json', 'w') as f:
        json.dump(updated_goals, f, indent=4)  # The 'indent' parameter makes the JSON file more readable with indentation

    updated_rewards = [reward.__dict__ for reward in rewards]
    with open('Rewards.json', 'w') as f:
        json.dump(updated_rewards, f, indent=4)

    global changes
    changes = False
    sg.popup_quick_message('Saved!', background_color = '#190b61')


    #Add and Remove Points
def add_remove_points(counter):
    """Manually add or remove an amount of points."""
    add_remove = sg.popup_get_text('How many points would you like to add? Type a negative number to subtract.')
    try:
        add_remove = int(add_remove)
        if counter + add_remove >= 0:
            counter += add_remove
            input_event = sg.popup_get_text('What are these points for?', 'Add to History')
            if input_event in ['', None]:
                input_event = 'No reason given'
            add_history(input_event, add_remove, counter)
            if add_remove >=0:
                sg.popup_quick_message(f'Added {add_remove} {"point" if add_remove == 1 else "points"}.', background_color = '#20471F')
            else:
                sg.popup_quick_message(f'Removed {abs(add_remove)} {"point" if add_remove == 1 else "points"}.', background_color = '#590409')
            return counter
        else:
            sg.popup('Insufficient points.')
    except:
        return counter

def add_history(event, value, counter):
    """Add something to the history tracker."""
    if value >= 0:
        value = (f'+{value}')
    if values['-Yesterday-'] == False:
        date = today.strftime('%m/%d/%Y')
    else:
        date = yesterday.strftime('%m/%d/%Y')
    new_history = (f'{date} | {event} | {value} | Total: {counter}')
    history.insert(1, new_history)
    global changes
    changes = True

def clear(clear_value):
    """Clear all points and history."""
    if type(clear_value) == int:
        clear_value = 0
        add_history('Reset all points', -abs(counter), 0)
    else:
        clear_value = ['POINT HISTORY:']
    global changes
    changes = True
    return clear_value

def add_edit_obj(obj_type, attributes = tuple()):
    """Add or edit a goal or reward. Receives attributes from edit_obj() if editing an existing object."""
    global changes
    if attributes: #If editing an existing object and attributes have been passed on, unpacks the tuple into separate variables
        name, max_points, min_points, note = attributes
    else: #If creating
        name = max_points = min_points = note = ''
    
    #Defining layout of the edit window
    minimum_visible = False if not attributes or min_points is None else True
    edit_layout = [
        [sg.Text(f'Please enter a name or short description for your {obj_type}.')],
        [sg.Input(name, key = '-Name-')],
        [sg.Checkbox(f'This {obj_type} has variable point values.', default = minimum_visible, enable_events = True, key = '-Variable_Points-', size = (30, 1))], #To hide the fields for variable point values
        [sg.Text(f'What is the minimum amount of points this reward can cost?' if obj_type == 'reward' else 'What is the minimum amount of points you can earn from this goal?', visible = minimum_visible, key = '-Minimum_Text-')],
        [sg.Input(min_points, key = '-Minimum-', visible = minimum_visible)],
        [sg.Text(f'How many points is this {obj_type} worth?', key = '-Maximum_Text-')],
        [sg.Input(max_points, key = '-Maximum-')],
        [sg.Text('Any additional notes? If not, leave blank.')],
        [sg.Input(note, key = '-Notes-')],
        [sg.Button('Submit'), sg.Button('Cancel')]
    ]
    edit_window = sg.Window(f'Create new {obj_type}' if not attributes else f'Edit {obj_type}', edit_layout)

    while True: #Main loop of edit window
        event, values = edit_window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            edit_window.close()
            return

        if values['-Variable_Points-'] == True: #Hide and unhide minimum points field with checkbox
            edit_window['-Minimum_Text-'].Update(visible = True)
            edit_window['-Minimum-'].Update(visible = True)
            edit_window['-Maximum_Text-'].Update('What is the maximum amount of points?')
            minimum_visible = True
        elif values['-Variable_Points-'] == False:
            edit_window['-Minimum_Text-'].Update(visible = False)
            edit_window['-Minimum-'].Update(visible = False)
            edit_window['-Maximum_Text-'].Update(f'How many points is this {obj_type} worth?')
            minimum_visible = False

        if event == 'Submit':
            edit_window.close()
            try:
                #Saving attributes
                name = values['-Name-']
                max_points = int(values['-Maximum-'])
                if values['-Minimum-'] in (None, '') or minimum_visible == False:
                    min_points = None
                else:
                    min_points = int(values['-Minimum-'])
                if values['-Notes-'] in (None, ''):
                    note = None
                else:
                    note = values['-Notes-']

                #Error handling 
                if name in (None, ''):
                    sg.popup_error('Must input a name!')
                    return None
                elif type(min_points) == int and (min_points >= max_points or min_points < 0) or max_points < 0:
                    sg.popup_error('Invalid point values.')
                    return None
                
                #Creating the object
                if attributes:
                    new_attributes = (name, max_points, min_points, note)
                    return new_attributes
                if obj_type == 'goal':
                    goal = Goal(name, max_points, min_points, note)
                    goals.append(goal)
                    changes = True
                    create_layout()
                    return
                elif obj_type == 'reward':
                    reward = Reward(name, max_points, min_points, note)
                    rewards.append(reward)
                    changes = True
                    create_layout()
                    return
                else:
                    raise Exception
            except:
                sg.popup_error(f'Unable to save {obj_type}!') #Nice job breaking it, hero
                return None

def create_layout():
    """Define the layout of the GUI"""
    global main_window, goals, rewards
    #Sorting goals and rewards by points then name
    goals = sorted(goals, key=lambda goal: (goal.max_points, goal.name))
    rewards = sorted(rewards, key=lambda reward: (reward.max_points, reward.name))

    #Make goal buttons
    goals_column = [ 
    [
        sg.Button(goal.name, size=(33, 1)),
        sg.Text(f"{f'{goal.min_points} - {goal.max_points}' if goal.min_points is not None else f'{goal.max_points}'} {'point' if goal.max_points == 1 else 'points'}",
                size=(12, 1),
                justification='center'),
        sg.Push(),
        sg.Button('ⓘ', key=f'goalinfo_{i}', visible = False if goal.note is None else True),
        sg.Button('✎', key=f'editgoal_{i}'),
        sg.Button('X', key=f'delgoal_{i}')
    ]
    for i, goal in enumerate(goals)
]

    #Make reward buttons
    rewards_column = [ 
        [
            sg.Button(reward.name, size=(33, 1)),
            sg.Text(f"{f'{reward.min_points} - {reward.max_points}' if reward.min_points is not None else f'{reward.max_points}'} {'point' if reward.max_points == 1 else 'points'}",
                    size=(12, 1),
                    justification='center'),
            sg.Push(),
            sg.Button('ⓘ', key=f'rewardinfo_{i}', visible = False if reward.note is None else True),
            sg.Button('✎', key=f'editreward_{i}'),
            sg.Button('X', key=f'delreward_{i}')
        ]
        for i, reward in enumerate(rewards)
    ]
    
    #Layout for tabs
    layout_goals_tab = [[sg.Push(), sg.Checkbox(f'Apply points to yesterday\'s date.', key = '-Yesterday-', size = (30, 1)), sg.Push()],
                        [sg.Column(layout = goals_column,
                        expand_x=True, expand_y=True,
                        scrollable = True, vertical_scroll_only = True, key = '-GOALTAB-')]]
    layout_rewards_tab = [[sg.Column(layout = rewards_column,
                        expand_x=True, expand_y=True, 
                        scrollable = True, vertical_scroll_only = True, key = '-REWARDTAB-')]]
    layout_history_tab = [[sg.Column(layout = [[ 
                            sg.Listbox(history,
                            size = (400, 500),
                            key = '-HISTORY-')]],
                            expand_x=True, expand_y=True,
                            )]]
    layout_options_tab = [[sg.Text('These changes will not save until the "Save" button is clicked.')],
                        [sg.Push(), sg.Button('Add a goal', size = (30, 1), key = 'addgoal'), sg.Push()],
                        [sg.Push(), sg.Button('Add a reward', size = (30, 1), key = 'addreward'), sg.Push()],
                        [sg.Push(), sg.Button('Reset points to 0', size = (30, 1)), sg.Push()],
                        [sg.Push(), sg.Button('Erase all history', size = (30, 1)), sg.Push()],
                        [sg.Push(), sg.Button('Rename points', size = (30, 1)), sg.Push()],
                        [sg.Push(), sg.Button('About Point Tracker', size = (30, 1)), sg.Push()]]
    tab_group = [[sg.Tab('Add Points', layout_goals_tab), sg.Tab('Redeem Rewards', layout_rewards_tab), sg.Tab('History', layout_history_tab), sg.Tab('Options', layout_options_tab)]]
    layout_frame = [
        [sg.Text('Total Points: ', size = (10, 1)), sg.Text(counter, size = (10, 1), key = '-POINTDISPLAY-'), sg.Push(), sg.Button('Add/Remove Points'),
        sg.Button('Save', size = (5, 1)), sg.Button('Exit', size = (5, 1))],
        [sg.TabGroup(tab_group)],
    ]
    main_layout = [
        [sg.Frame(points_name, layout_frame)],
    ]
    if window_initialized == True: #Closes the window when updating the layout, so it doesn't spawn multiple copies
        main_window.close()
    main_window = sg.Window('Point Tracker', main_layout, finalize = True, enable_close_attempted_event = True, size = (600, 700), resizable = True)

create_layout()

#Main event loop
while True:
    window_initialized = True
    event, values = main_window.read() #Read inputs from the window

    for goal in goals: #Add points when clicking a goal
        if event == goal.name:
            counter = goal.add_counter(counter)

    for reward in rewards: #Subtract points when clicking a reward
        if event == reward.name:
            counter = reward.subtract_counter(counter)

    if event == 'Add/Remove Points':
        counter = add_remove_points(counter)

    #Goal/reward info button
    if event.startswith('goalinfo'):
        goal_index = int(event.split('_')[-1])
        goals[goal_index].info_button()
    if event.startswith('rewardinfo'):
        reward_index = int(event.split('_')[-1])
        rewards[reward_index].info_button()

    if event == 'Save' or event == 'Save changes': #Save updated point count and history
        save()
    
    if event == 'Reset points to 0':
        confirm = sg.popup_yes_no('Are you sure you want to reset your points?', title = 'Reset?')
        if confirm == 'Yes':
            counter = clear(counter)
        else:
            continue
    if event == 'Erase all history':
        confirm = sg.popup_yes_no('Are you sure you want to clear all of your history?', title = 'Reset?')
        if confirm == 'Yes':
            history = clear(history)
        else:
            continue

    if event == 'addgoal': #Add a new goal
        add_edit_obj('goal')
    if event == 'addreward':
        add_edit_obj('reward')

    if event.startswith('editgoal_'): #Edit an existing goal
        obj_index = int(event.split('_')[-1]) #Find the index of the object in the list
        goals[obj_index].edit_obj() #Call for the object at that index to be edited
    if event.startswith('editreward_'):
        obj_index = int(event.split('_')[-1])
        rewards[obj_index].edit_obj()

    if event.startswith('delgoal_'):
        goal_index = int(event.split('_')[-1])
        goal_to_delete = goals[goal_index]
        goal_to_delete.del_object(goals)
        continue
    if event.startswith('delreward_'):
        reward_index = int(event.split('_')[-1])
        reward_to_delete = rewards[reward_index]
        reward_to_delete.del_object(rewards)
        continue

    if event == 'Rename points':
        new_points_name = sg.popup_get_text('What are these points called?', points_name)
        points_name = new_points_name if new_points_name not in ['', None] else points_name
        changes = True
        create_layout()

    if event == 'About Point Tracker':
        sg.popup(f'''Welcome to Point Tracker v{version}!
To add goals and rewards, click the Options tab and follow the prompts.
Clicking the name of a goal or reward will add or subtract points from your total.
Make sure you save before closing the application! If you close the application without saving, all your changes will be lost.
If you have any questions or bug reports, reach out to me at maxwebsites13@gmail.com.
Enjoy!
''', title = 'About Point Tracker')


    main_window['-POINTDISPLAY-'].update(str(counter)) #Update point counter
    main_window['-HISTORY-'].update(values = history) #Update history list

    if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == 'Exit':
        if changes:
            save_quit = sg.popup_yes_no('Would you like to save your changes?')
            if save_quit == 'Yes':
                save()
            elif save_quit == None:
                continue
        break

main_window.close()

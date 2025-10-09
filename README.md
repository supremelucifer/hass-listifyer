    
<p align="center">
  <img width="150" alt="listifyer" src="https://github.com/user-attachments/assets/93a023fa-3e92-4155-8bd4-e2a513ddd152">
  <br><br>
  <a href="https://play.google.com/store/apps/details?id=com.dimitri.listifyer" target="_blank">
    <img alt="Get it on Google Play" src="https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png" width="200"/>
  </a>
</p>

  

# Listifyer for Home Assistant

This is the official Home Assistant integration for the Listifyer App.

## Installation via HACS

1.  Ensure you have [HACS (Home Assistant Community Store)](https://hacs.xyz/) installed.
2.  In Home Assistant, navigate to **HACS > Integrations**.
3.  Click the three dots in the top right corner and select **Custom repositories**.
4.  Paste the URL of this GitHub repository into the field, select the category **Integration**, and click **Add**.
5.  The "Listifyer" integration will now appear in your list. Click **Install**.
6.  Restart Home Assistant when prompted by HACS.

## App configuration

In the Listifyer app, first go to "Settings" and then navigate to the "Plugins" tab. Select "Home Assistant" and enter the URL of your Home Assistant instance (preferably the remote URL) and a Long-Lived Access Token.

Once you have filled in all the details, you need to perform a one-time force full synchronization. After that, Home Assistant will be updated automatically as soon as you adjust something in the app.

## Configuration

After installation and restarting, you can add the integration. Click the button below to go directly to the configuration page.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=listifyer)

---

## Usage Examples

Here are some example Lovelace cards you can create using the sensors provided by the Listifyer integration. You can copy and paste this code into a 'Manual Card' on your dashboard.

<details>
<summary><b>Example: Pending Bills for the Current Month</b></summary>

    type: markdown
    title: Pending Bills
    content: |
      {% set ns = namespace(bills=[]) %}
      {% for bill in state_attr('sensor.listifyer_bills', 'items') %}
        {% for date, paid in bill.paymentLog.items() %}
          {% if now().strftime('%Y-%m') in date and not paid %}
            {% set ns.bills = ns.bills + [bill] %}
          {% endif %}
        {% endfor %}
      {% endfor %}
      {% set sorted_bills = ns.bills | sort(attribute='dueDay') %}
      {% if sorted_bills | length > 0 %}
      {% for bill in sorted_bills -%}
      {{ bill.title }}: €{{ "%.2f"|format(bill.amount) }}
      {% endfor %}
      {% else %}
      No pending bills.
      {% endif %}

</details>


<details>
<summary><b>Example: Series Progress Tracker</b></summary>

    type: markdown
    title: Series I'm Watching
    icon: mdi:television-play
    content: |
      {% set ns = namespace(series_to_watch=[]) %}
      {% for item in state_attr('sensor.listifyer_media_items', 'items') %}
        {% if item.type == 'SERIES' and item.currentSeason is defined and item.currentEpisode is defined %}
          {% set ns.series_to_watch = ns.series_to_watch + [item] %}
        {% endif %}
      {% endfor %}
      {% set sorted_series = ns.series_to_watch | sort(attribute='title') %}
      {% if sorted_series | length > 0 %}
      <table>
      {% for serie in sorted_series %}
        <tr>
          <td style="padding-right: 15px; padding-bottom: 10px;">
            <img src="{{ serie.imageUrl }}" width="50" style="border-radius: 4px;">
          </td>
          <td valign="middle" style="padding-bottom: 10px;">
            <b>{{ serie.title }}</b><br>
            <font color="grey">S{{ '%02d' | format(serie.currentSeason) }}E{{ '%02d' | format(serie.currentEpisode) }}</font>
          </td>
        </tr>
      {% endfor %}
      </table>
      {% else %}
      You are not currently tracking any series.
      {% endif %}

</details>

<details>
<summary><b>Example: Shopping List</b></summary>

    type: markdown
    title: Shopping List
    icon: mdi:cart
    content: >-
      {% set ns = namespace(todo=[], done=[]) %}
      {% set all_items = state_attr('sensor.listifyer_shopping_list', 'items') %}
      {%- for item in all_items -%}
        {%- if item.isChecked | default(false) -%}
          {%- set ns.done = ns.done + [item] -%}
        {%- else -%}
          {%- set ns.todo = ns.todo + [item] -%}
        {%- endif -%}
      {%- endfor -%}
      {%- if all_items | length > 0 -%}
        {%- for category in ns.todo | groupby('category') | sort(attribute='grouper') -%}
          <h4 style="margin-bottom: 2px; margin-top: 15px;">{{ category.grouper }}</h4>
          {%- for item in category.list -%}
            <div style="padding-left: 5px; padding-top: 5px; font-size: 16px;">
              ☐ {{ item.name }}
            </div>
          {%- endfor -%}
        {%- endfor -%}
        {%- if ns.done | length > 0 -%}
          <hr style="border: 1px solid #282828; margin-top: 25px; margin-bottom: 0px;">
          <details style="margin-top: 15px;">
            <summary>✅ Checked ({{ ns.done | length }})</summary>
            {%- for item in ns.done -%}
              <div style="padding-left: 5px; padding-top: 5px; font-size: 15px;">
                 <span style="color: grey; text-decoration: line-through;">{{ item.name }}</span>
              </div>
            {%- endfor -%}
          </details>
        {%- endif -%}
      {%- else -%}
        🎉 The shopping list is empty!
      {%- endif -%}

</details>

<details>
<summary><b>Example: To-Do List</b></summary>

    type: markdown
    title: To-Do List
    icon: mdi:check-circle-outline
    content: >-
      {% set ns = namespace(todo=[], done=[]) %}
      {% set all_items = state_attr('sensor.listifyer_todo_list', 'items') %}
      {%- for item in all_items -%}
        {%- if item.isDone | default(false) -%}
          {%- set ns.done = ns.done + [item] -%}
        {%- else -%}
          {%- set ns.todo = ns.todo + [item] -%}
        {%- endif -%}
      {%- endfor -%}
      {%- if all_items | length > 0 -%}
        {%- for category in ns.todo | groupby('category') | sort(attribute='grouper') -%}
          <h4 style="margin-bottom: 5px; margin-top: 15px;">{{ category.grouper }}</h4>
          {%- for task in category.list | sort(attribute='task') -%}
            <div style="padding-bottom: 12px; margin-bottom: 12px; {% if not loop.last %} border-bottom: 1px solid #393939; {% endif %}">
              <div style="padding-top: 8px;">
                <b style="font-size: 16px;">☐ {{ task.task }}</b>
              </div>
              {%- if task.dueDate is defined and task.dueDate is not none -%}
                <div style="padding-left: 25px; padding-top: 4px; color: grey; font-size: 14px;">
                  🗓️ Due: {{ as_timestamp(task.dueDate) | timestamp_custom('%-d %B %Y') }}
                </div>
              {%- endif -%}
              {%- if task.subTasks is defined and task.subTasks | count > 0 -%}
                {%- for subtask in task.subTasks -%}
                  <div style="padding-left: 25px; padding-top: 5px;">
                    {%- if subtask.isChecked | default(false) -%}
                      <span style="color: grey; text-decoration: line-through;">✅ {{ subtask.text }}</span>
                    {%- else -%}
                      <span>☐ {{ subtask.text }}</span>
                    {%- endif -%}
                  </div>
                {%- endfor -%}
              {%- endif -%}
            </div>
          {%- endfor -%}
        {%- endfor -%}
        {%- if ns.done | length > 0 -%}
          <hr style="border: 1px solid #282828; margin-top: 25px; margin-bottom: 0px;">
          <details style="margin-top: 15px;">
            <summary>✅ Completed ({{ ns.done | length }})</summary>
            {%- for task in ns.done | sort(attribute='task') -%}
              <div style="padding-left: 5px; padding-top: 8px;">
                 <span style="color: grey; text-decoration: line-through;">{{ task.task }}</span>
              </div>
            {%- endfor -%}
          </details>
        {%- endif -%}
      {%- else -%}
        🎉 Your to-do list is empty!
      {%- endif -%}

</details>

<details>
<summary><b>Example: Meal Planner</b></summary>

    type: markdown
    title: Meal Plan
    icon: mdi:silverware-fork-knife
    content: >-
      {% set meal_plan_item = state_attr('sensor.listifyer_meal_plan', 'item') -%}
      {% if meal_plan_item and meal_plan_item.plan -%}
        {% set plan_data = meal_plan_item.plan -%}
        {% set week_number = meal_plan_item.planForWeek -%}
        {% set day_order = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'] -%}
        {% set day_names = {'MONDAY': 'Monday', 'TUESDAY': 'Tuesday', 'WEDNESDAY': 'Wednesday', 'THURSDAY': 'Thursday', 'FRIDAY': 'Friday', 'SATURDAY': 'Saturday', 'SUNDAY': 'Sunday'} -%}
        {% set meal_order = ['BREAKFAST', 'LUNCH', 'DINNER'] -%}
        {% set meal_icons = {'BREAKFAST': 'mdi:weather-sunset', 'LUNCH': 'mdi:white-balance-sunny', 'DINNER': 'mdi:weather-night'} -%}
        <h2 style="text-align:center; margin-bottom: 20px;">Week {{ week_number }}</h2>
        {% for day_key in day_order -%}
          {% if plan_data[day_key] is defined -%}
            <h3 style="margin-top: 20px;">{{ day_names[day_key] }}</h3>
            <table style="width: 100%; border-collapse: collapse;">
            {%- for meal_key in meal_order -%}
              {%- if plan_data[day_key][meal_key] is defined and plan_data[day_key][meal_key] | count > 0 -%}
                {%- set recipe = plan_data[day_key][meal_key][0] -%}
                <tr style="border-bottom: 1px solid #393939;">
                  <td style="width: 30px; text-align: center; padding: 10px 5px 10px 0px;"><ha-icon icon="{{ meal_icons[meal_key] }}" style="color: grey;"></ha-icon></td>
                  <td style="width: 60px; padding: 10px 10px 10px 5px;"><img src="{{ recipe.imageIdentifier }}" width="50" style="border-radius: 4px; display: block;"></td>
                  <td style="vertical-align: middle; font-size: 14px; white-space: normal;">{{ recipe.title }}</td>
                </tr>
              {%- endif -%}
            {%- endfor -%}
            </table>
          {%- endif -%}
        {%- endfor -%}
      {% else -%}
        🍴 There is no meal plan for this week yet.
      {%- endif %}

</details>

<details>
<summary><b>Example: Today's Appointments</b></summary>

    type: markdown
    content: >
      {% set today_str = now().strftime('%Y-%-m-%d') %}
      {% set now_dt = now() %}
      {% set appointments = state_attr('sensor.listifyer_appointments', 'items')
                           | selectattr('date', 'eq', today_str)
                           | sort(attribute='startTime')
                           | list %}
      {% set found_next = namespace(value=false) %}

      **Today, {{ now().strftime('%-d %B %Y') }}**

      {% if appointments %}
        {% for item in appointments %}
          {% set naive_start_dt = strptime(item.date ~ ' ' ~ item.startTime, '%Y-%m-%d %H:%M') %}
          {% set naive_end_dt = strptime(item.date ~ ' ' ~ item.endTime, '%Y-%m-%d %H:%M') %}
          {% if item.endTime < item.startTime %}
            {% set naive_end_dt = naive_end_dt + timedelta(days=1) %}
          {% endif %}
          {% set start_dt = naive_start_dt.replace(tzinfo=now_dt.tzinfo) %}
          {% set end_dt = naive_end_dt.replace(tzinfo=now_dt.tzinfo) %}
          {% set is_in_progress = start_dt <= now_dt and end_dt > now_dt %}
          {% set is_past = end_dt <= now_dt %}
          {% set is_next = not found_next.value and start_dt > now_dt %}

          {% if is_in_progress %}
      🟢 **{{ item.startTime }} - {{ item.endTime }}** (In progress)
      *{{ item.title | replace('"', '') }}*
            {% set found_next.value = true %}
          {% elif is_past %}
      ✅ **{{ item.startTime }} - {{ item.endTime }}** (Finished)
      *{{ item.title | replace('"', '') }}*
          {% elif is_next %}
      ⏰ **{{ item.startTime }} - {{ item.endTime }}** (Next up)
      *{{ item.title | replace('"', '') }}*
            {% set found_next.value = true %}
          {% else %}
      🗓️ **{{ item.startTime }} - {{ item.endTime }}**
      *{{ item.title | replace('"', '') }}*
          {% endif %}
          {% if not loop.last %}
      ---
          {% endif %}
        {% endfor %}
      {% else %}
        🗓️ *No appointments for today.*
      {% endif %}

</details>

<details>
<summary><b>Example: Recipes</b></summary>

    type: markdown
    content: >
      # 🍽️ Recipes
      _Click on a recipe to expand._
      ---
      {% for recipe in state_attr('sensor.listifyer_recipes', 'items') | sort(attribute='title') %}
      <details>
        <summary><b>{{ recipe.title }}</b></summary>
        {% if 'imageIdentifier' in recipe and recipe.imageIdentifier and recipe.imageIdentifier.startswith('http') %}
        ![{{ recipe.title }}]({{ recipe.imageIdentifier }})
        {% endif %}
        ### 🥕 Ingredients
        {% for line in recipe.ingredients.split('\n') if line|trim != '' %}
        - {{ line | regex_replace('<[^>]+>', '') | trim }}
        {% endfor %}
        ### 👨‍🍳 Instructions
        {% for step in recipe.instructions.split('\n') if step|trim != '' %}
        {{ loop.index }}. {{ step | regex_replace('<[^>]+>', '') | trim }}
        {% endfor %}
        {% if 'sourceUrl' in recipe and recipe.sourceUrl %}
        🔗 [View original recipe]({{ recipe.sourceUrl }})
        {% endif %}
      </details>
      <hr>
      {% endfor %}

</details>

<details>
<summary><b>Example: Pantry Items</b></summary>

    type: markdown
    title: Pantry Items
    content: |
      {% for item in state_attr('sensor.listifyer_pantry_items', 'items') %}
      - {{ item.name | trim }}: {{ item.quantity }}
      {% endfor %}

</details>

<details>
<summary><b>Example: Notes</b></summary>

    type: markdown
    title: Notes
    content: |
      {% for note in state_attr('sensor.listifyer_notes', 'items') %}
      {% if note.get('status') != 'ARCHIVED' %}
      {% if not loop.first %}
      ***
      {% endif %}
      **{% if note.get('isPinned') %}📌 {% endif %}{{ note.title }}**
      {{ note.content | replace('\n', '  \n') }}
      {% if note.tags %}
      > _#{{ note.tags | join(' #') }}_
      {% endif %}
      {% endif %}
      {% endfor %}

</details>

<details>
<summary><b>Example: Wishlist</b></summary>

    type: markdown
    title: Wishlist
    content: |
      {% for item in state_attr('sensor.listifyer_wishlist', 'items') %}
        {% if not loop.first %}
        ***
        {% endif %}
        <a href="{{ item.sourceUrl }}" target="_blank" style="text-decoration: none; color: var(--primary-text-color); display: block; overflow: auto;">
          <img src="{{ item.imageIdentifier }}" style="float: left; width: 100px; border-radius: 5px; margin-right: 12px; margin-bottom: 4px;">
          <b>{{ item.name }}</b>
          <br>
          <small>{{ item.description }}</small>
        </a>
      {% endfor %}

</details>

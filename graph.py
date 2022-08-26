import streamlit as st
import matplotlib.pyplot as plt
import sqlite3


con = sqlite3.connect('practice.db')
cur = con.cursor()
#fetch last 7 days data            
cur.execute("SELECT day, recognition, blink_count FROM EYEDATA ORDER BY day DESC limit 7")
data = cur.fetchall()
day = []
recognition = []
blink_count = []
for row in data:
    day.append(row[0])
    recognition.append(row[1])
    blink_count.append(row[2])

#rearrangement datas
day.reverse()
recognition.reverse()
blink_count.reverse()
fig, ax = plt.subplots()
ax.bar(day, blink_count, color = 'green', alpha = 0.3)
ax2 = ax.twinx()
ax2.plot(day, recognition, color = 'purple')      
for i in range(0, len(day)):
    ax2.text(i, recognition[i], recognition[i], color='purple', size=15, ha="left")
    ax.text(i, blink_count[i], blink_count[i], color='green', size=13, ha="right")
plt.rc('xtick', labelsize = 7)
ax.set_ylabel('blink count')
ax.set_xlabel('day')
ax2.set_ylabel('recognition time')
#show()

st.pyplot(fig)
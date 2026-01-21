with open('app/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the ASK_VIDEOS section start
start_idx = None
for i, line in enumerate(lines):
    if 'if state == "ASK_VIDEOS":' in line:
        start_idx = i
        break

# Find the end (before '# If already done:')
end_idx = None
for i in range(start_idx, len(lines)):
    if '# If already done:' in lines[i]:
        end_idx = i
        break

print(f"Found section from line {start_idx} to {end_idx}")

# Replace the section
new_section = """    if state == "ASK_VIDEOS":
        wants_videos = normalize_yes_no(text) == "Yes"
        data["wants_videos"] = wants_videos
        session["state"] = "DONE"
        
        if wants_videos:
            # Retrieve stored recommendation and add videos
            rec = session.get("recommendation")
            if rec:
                # Get YouTube videos
                rec_with_videos = recommender.recommend(
                    profile={
                        "sex": data["sex"],
                        "age": data["age"],
                        "height_m": data["height_m"],
                        "weight_kg": data["weight_kg"],
                        "hypertension": data["hypertension"],
                        "diabetes": data["diabetes"],
                    },
                    wants_videos=True
                )
                
                msg = "▶️ Here are some suggested YouTube workout videos:\\n\\n"
                if rec_with_videos["workouts"]:
                    for w in rec_with_videos["workouts"]:
                        msg += f"• {w['title']} ({w['duration']} min)\\n  {w['youtube_link']}\\n\\n"
                    msg += "Good luck with your fitness journey! 💪"
                else:
                    msg = "I couldn't find specific videos at the moment, but good luck with your fitness journey! 💪"
            else:
                msg = "Good luck with your fitness journey! 💪"
        else:
            msg = "No problem! Good luck with your fitness journey! 💪"

        return ChatMessageResponse(
            session_id=payload.session_id,
            state=session["state"],
            data_collected=data,
            message=msg
        )

"""

# Reconstruct the file
new_lines = lines[:start_idx] + [new_section] + lines[end_idx:]

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Successfully updated ASK_VIDEOS section!')

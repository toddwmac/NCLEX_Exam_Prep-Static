from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import markdown
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Question bank
QUESTIONS = {
    'med-surg': [
        {
            'id': 'ms1',
            'question': 'A client with COPD is receiving oxygen therapy at 2 L/min via nasal cannula. Which assessment finding would indicate the therapy is effective?',
            'options': [
                'Oxygen saturation of 88%',
                'Respiratory rate of 28 breaths/min',
                'Oxygen saturation of 95%',
                'Use of accessory muscles'
            ],
            'correct': 2,
            'explanation': 'An oxygen saturation of 95% indicates effective oxygen therapy. For COPD patients, target saturation is typically 88-92%, but higher values are acceptable if the patient is stable.'
        },
        {
            'id': 'ms2',
            'question': 'A client with diabetes mellitus has a blood glucose level of 45 mg/dL. Which intervention should the nurse implement first?',
            'options': [
                'Administer glucagon IM',
                'Give 15g of fast-acting carbohydrate',
                'Call the healthcare provider',
                'Check vital signs'
            ],
            'correct': 1,
            'explanation': 'For conscious patients with hypoglycemia, the first intervention is to provide 15g of fast-acting carbohydrate (like juice or glucose tablets), then recheck blood glucose in 15 minutes.'
        },
        {
            'id': 'ms3',
            'question': 'A client with heart failure is experiencing dyspnea and peripheral edema. Which position should the nurse place the client in first?',
            'options': [
                'Left lateral recumbent',
                'Supine with legs elevated',
                'High Fowler\'s position',
                'Prone position'
            ],
            'correct': 2,
            'explanation': 'High Fowler\'s position (sitting upright at 60-90 degrees) helps reduce dyspnea by allowing for maximum lung expansion and reducing venous return to the heart, which helps decrease pulmonary congestion.'
        },
        {
            'id': 'ms4',
            'question': 'A client with acute pancreatitis is experiencing severe abdominal pain. Which nursing intervention should be implemented first?',
            'options': [
                'Administer prescribed pain medication',
                'Place the client in a side-lying position',
                'Assess pain characteristics',
                'Apply a heating pad to the abdomen'
            ],
            'correct': 2,
            'explanation': 'Before implementing any intervention, the nurse must first assess the pain characteristics (OLDCARTS) to establish a baseline and determine the most appropriate intervention.'
        },
        {
            'id': 'ms5',
            'question': 'A client post-thyroidectomy suddenly develops difficulty breathing and swelling around the neck. What is the priority nursing action?',
            'options': [
                'Apply an ice pack to the neck',
                'Call the surgeon',
                'Prepare for emergency tracheostomy',
                'Loosen or remove neck dressings'
            ],
            'correct': 3,
            'explanation': 'Neck swelling post-thyroidectomy could indicate hematoma formation, which can compromise the airway. The immediate action is to loosen or remove dressings to relieve pressure while preparing for possible emergency intervention.'
        }
    ],
    'pediatrics': [
        {
            'id': 'ped1',
            'question': 'A 2-year-old child presents with a fever of 103°F (39.4°C). Which intervention should the nurse implement first?',
            'options': [
                'Administer acetaminophen as prescribed',
                'Apply a cold compress to the forehead',
                'Encourage increased fluid intake',
                'Place the child in a lukewarm bath'
            ],
            'correct': 0,
            'explanation': 'The first intervention for a high fever should be to administer antipyretic medication as prescribed. This helps reduce fever and provides comfort to the child.'
        },
        {
            'id': 'ped2',
            'question': 'Which finding in a 6-month-old infant would indicate normal development?',
            'options': [
                'Walks with assistance',
                'Sits without support',
                'Speaks in two-word sentences',
                'Feeds self with spoon'
            ],
            'correct': 1,
            'explanation': 'At 6 months, sitting without support is a normal developmental milestone. Walking, speaking in sentences, and self-feeding with utensils come at later stages.'
        },
        {
            'id': 'ped3',
            'question': 'A 4-year-old is admitted with suspected appendicitis. Which assessment finding is most concerning?',
            'options': [
                'Temperature of 99.5°F (37.5°C)',
                'Rebound tenderness in right lower quadrant',
                'Decreased appetite',
                'Complaints of nausea'
            ],
            'correct': 1,
            'explanation': 'Rebound tenderness in the right lower quadrant is a significant finding indicating peritoneal inflammation, which is a key indicator of appendicitis requiring immediate medical attention.'
        },
        {
            'id': 'ped4',
            'question': 'When administering oral medication to a 2-year-old, which approach is most appropriate?',
            'options': [
                'Mix the medication with a full cup of juice',
                'Use a medication dropper or oral syringe',
                'Have child swallow pills with water',
                'Mix medication in full portion of food'
            ],
            'correct': 1,
            'explanation': 'A medication dropper or oral syringe provides the most accurate dosing and best control for administering oral medications to young children, ensuring they receive the full dose.'
        },
        {
            'id': 'ped5',
            'question': 'A 3-month-old infant has been diagnosed with respiratory syncytial virus (RSV). Which finding requires immediate intervention?',
            'options': [
                'Slight nasal congestion',
                'Low-grade fever',
                'Decreased feeding',
                'Nasal flaring and retractions'
            ],
            'correct': 3,
            'explanation': 'Nasal flaring and retractions are signs of respiratory distress in infants and require immediate intervention as they indicate increased work of breathing and potential respiratory failure.'
        }
    ],
    'mental-health': [
        {
            'id': 'mh1',
            'question': 'A client with depression states, "I just want to end it all." What is the nurse\'s best initial response?',
            'options': [
                'Don\'t talk like that; things will get better.',
                'Are you having thoughts of hurting yourself?',
                'Let me call your family right away.',
                'You need to think more positively.'
            ],
            'correct': 1,
            'explanation': 'The best initial response is to directly assess suicide risk by asking about self-harm thoughts. This shows you take the client seriously and allows for proper assessment.'
        },
        {
            'id': 'mh2',
            'question': 'A client with schizophrenia reports that the TV is sending special messages. Which response by the nurse is most therapeutic?',
            'options': [
                'That must be frightening for you.',
                'The TV isn\'t really sending you messages.',
                'Let\'s watch something else.',
                'Who else knows about these messages?'
            ],
            'correct': 0,
            'explanation': 'Acknowledging the client\'s feelings without reinforcing or challenging the delusion is most therapeutic. This builds trust while maintaining a reality-based relationship.'
        },
        {
            'id': 'mh3',
            'question': 'A client with bipolar disorder in manic phase is pacing the unit and talking rapidly. What is the priority nursing intervention?',
            'options': [
                'Provide complex activities',
                'Create a calm, low-stimulus environment',
                'Encourage socialization with others',
                'Begin group therapy session'
            ],
            'correct': 1,
            'explanation': 'For a client in manic phase, reducing environmental stimuli is priority to help decrease agitation and promote calm behavior. This helps prevent escalation and supports emotional regulation.'
        },
        {
            'id': 'mh4',
            'question': 'A client with anxiety is practicing deep breathing exercises. Which observation indicates the technique is effective?',
            'options': [
                'Respiratory rate increases to 24/min',
                'Client reports feeling lightheaded',
                'Shoulder muscles appear more relaxed',
                'Client maintains conversation during exercise'
            ],
            'correct': 2,
            'explanation': 'Relaxation of shoulder muscles indicates effective deep breathing technique as it shows reduced physical tension and successful anxiety reduction.'
        },
        {
            'id': 'mh5',
            'question': 'A client with anorexia nervosa states, "I\'m too fat to eat lunch today." Which response is most therapeutic?',
            'options': [
                '"You\'re actually underweight for your height."',
                '"Let\'s talk about your feelings right now."',
                '"You must eat to leave the hospital."',
                '"Everyone needs to eat lunch."'
            ],
            'correct': 1,
            'explanation': 'Exploring feelings is most therapeutic as it addresses the emotional component of the eating disorder rather than challenging the distorted body image or using coercion.'
        }
    ],
    'maternal': [
        {
            'id': 'mat1',
            'question': 'A primigravida in active labor has contractions every 3 minutes. Which finding indicates that labor is progressing normally?',
            'options': [
                'Cervical dilation decreasing',
                'Contractions becoming irregular',
                'Cervical dilation of 1 cm per hour',
                'Fetal station remaining at -2'
            ],
            'correct': 2,
            'explanation': 'Normal labor progression in the active phase is characterized by cervical dilation of approximately 1 cm per hour in primigravidas.'
        },
        {
            'id': 'mat2',
            'question': 'Which assessment finding in a 2-hour-old newborn requires immediate nursing intervention?',
            'options': [
                'Respiratory rate of 40 breaths/min',
                'Axillary temperature of 98.6°F (37°C)',
                'Heart rate of 180 beats/min',
                'Clear lung sounds bilaterally'
            ],
            'correct': 2,
            'explanation': 'A heart rate of 180 beats/min in a newborn is tachycardia and requires immediate attention. Normal newborn heart rate is 120-160 beats/min.'
        },
        {
            'id': 'mat3',
            'question': 'A postpartum client has a temperature of 101.2°F (38.4°C) 24 hours after delivery. What is the priority nursing action?',
            'options': [
                'Administer acetaminophen',
                'Assess lochia and fundus',
                'Encourage increased fluids',
                'Monitor vital signs every 4 hours'
            ],
            'correct': 1,
            'explanation': 'Assessing lochia and fundus is priority as postpartum fever could indicate endometritis or other infection. The character of lochia and fundal assessment provide crucial information about potential complications.'
        },
        {
            'id': 'mat4',
            'question': 'During a prenatal visit at 32 weeks gestation, the client reports severe headache and visual changes. What should the nurse assess first?',
            'options': [
                'Fetal movement',
                'Blood pressure',
                'Urine protein',
                'Deep tendon reflexes'
            ],
            'correct': 1,
            'explanation': 'Blood pressure should be assessed first as severe headache and visual changes in the third trimester are concerning symptoms of preeclampsia, where hypertension is a key diagnostic criterion.'
        },
        {
            'id': 'mat5',
            'question': 'A client 2 hours postpartum has a blood pressure of 82/50 mmHg and bright red vaginal bleeding. Which intervention is priority?',
            'options': [
                'Massage fundus',
                'Start IV fluids',
                'Check hemoglobin level',
                'Administer oxytocin'
            ],
            'correct': 0,
            'explanation': 'Fundal massage is the priority intervention as it helps the uterus contract, potentially stopping the hemorrhage which is likely causing the hypotension. This addresses the root cause while other interventions are supportive.'
        }
    ],
    'pharmacology': [
        {
            'id': 'pharm1',
            'question': 'A client is prescribed warfarin (Coumadin). Which food should the nurse teach the client to avoid?',
            'options': [
                'Bananas',
                'Green leafy vegetables',
                'Lean meats',
                'White bread'
            ],
            'correct': 1,
            'explanation': 'Green leafy vegetables are high in vitamin K, which antagonizes the anticoagulant effect of warfarin. Clients should maintain consistent vitamin K intake.'
        },
        {
            'id': 'pharm2',
            'question': 'A client taking furosemide (Lasix) requires which laboratory value to be monitored most closely?',
            'options': [
                'Potassium',
                'Calcium',
                'Magnesium',
                'Phosphorus'
            ],
            'correct': 0,
            'explanation': 'Furosemide is a loop diuretic that causes increased potassium excretion, potentially leading to hypokalemia. Potassium levels must be monitored closely.'
        },
        {
            'id': 'pharm3',
            'question': 'A client is receiving vancomycin IV. Which assessment is most important to monitor?',
            'options': [
                'Blood glucose levels',
                'Kidney function tests',
                'Liver function tests',
                'Platelet count'
            ],
            'correct': 1,
            'explanation': 'Kidney function tests are most important to monitor as vancomycin can cause nephrotoxicity. Regular monitoring of kidney function helps prevent or identify renal damage early.'
        },
        {
            'id': 'pharm4',
            'question': 'A client taking lithium presents with tremors, diarrhea, and vomiting. What is the priority nursing action?',
            'options': [
                'Administer the next scheduled dose',
                'Check lithium level immediately',
                'Encourage increased fluid intake',
                'Monitor vital signs only'
            ],
            'correct': 1,
            'explanation': 'These symptoms suggest lithium toxicity, which can be life-threatening. Checking lithium levels immediately is priority to determine the severity and guide treatment.'
        },
        {
            'id': 'pharm5',
            'question': 'When administering subcutaneous insulin, which technique is most important?',
            'options': [
                'Using alcohol to clean the site',
                'Rotating injection sites',
                'Aspirating before injection',
                'Massaging the site after'
            ],
            'correct': 1,
            'explanation': 'Rotating injection sites is most important to prevent lipohypertrophy, which can affect insulin absorption and glycemic control.'
        }
    ],
    'leadership': [
        {
            'id': 'lead1',
            'question': 'Which task is most appropriate for the charge nurse to delegate to a licensed practical nurse (LPN)?',
            'options': [
                'Initial patient assessment',
                'Care plan development',
                'Medication administration',
                'Patient teaching'
            ],
            'correct': 2,
            'explanation': 'LPNs can safely administer most medications within their scope of practice. Initial assessments, care planning, and patient teaching are typically RN responsibilities.'
        },
        {
            'id': 'lead2',
            'question': 'A nurse observes a colleague making a medication error. What is the first action the nurse should take?',
            'options': [
                'Report the colleague to the nurse manager',
                'Document the error in the incident report',
                'Ensure the patient\'s safety',
                'Notify the physician'
            ],
            'correct': 2,
            'explanation': 'The first priority is always patient safety. After ensuring the patient is safe, the error should be reported and documented according to facility policy.'
        },
        {
            'id': 'lead3',
            'question': 'The charge nurse is assigning patients. Which client should be assigned to the new graduate nurse?',
            'options': [
                'Stable post-operative day 2 client',
                'Client requiring complex wound care',
                'Client with multiple drips',
                'Unstable cardiac client'
            ],
            'correct': 0,
            'explanation': 'A stable post-operative client is most appropriate for a new graduate nurse as it provides opportunity for skill development while ensuring patient safety.'
        },
        {
            'id': 'lead4',
            'question': 'A nurse notices a colleague frequently arriving late and making medication errors. What is the best initial action?',
            'options': [
                'Report to nursing administration',
                'Discuss concerns directly with colleague',
                'Document all observed incidents',
                'Report to state board of nursing'
            ],
            'correct': 1,
            'explanation': 'Speaking directly with the colleague first is most professional and may reveal underlying issues that can be addressed before escalating to higher authorities.'
        },
        {
            'id': 'lead5',
            'question': 'When implementing a new bedside procedure, which approach is most effective?',
            'options': [
                'Send email with new protocol',
                'Post notice on bulletin board',
                'Provide hands-on training sessions',
                'Leave instruction sheets at stations'
            ],
            'correct': 2,
            'explanation': 'Hands-on training sessions are most effective for implementing new procedures as they allow for demonstration, practice, and immediate feedback while ensuring competency.'
        }
    ]
}

def load_study_guide(guide_name):
    # First try loading from static/content/study-guides
    md_path = os.path.join('static', 'content', 'study-guides', f'{guide_name}.md')
    if os.path.exists(md_path):
        with open(md_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Convert Markdown to HTML with extended features
            html_content = markdown.markdown(content, extensions=[
                'fenced_code',
                'tables',
                'toc',
                'attr_list',
                'def_list',
                'footnotes'
            ])
            return html_content
    
    # Fall back to template if exists
    html_path = os.path.join('templates', f'{guide_name}.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    return None

def load_quick_reference(reference_name):
    file_path = os.path.join('static', 'content', 'quick-reference', f'{reference_name}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/practice')
def practice():
    topic = request.args.get('topic')
    if topic and topic in QUESTIONS:
        return render_template('question.html', topic=topic, questions=QUESTIONS[topic])
    return render_template('practice.html')

@app.route('/materials')
def materials():
    return render_template('materials.html')

@app.route('/materials/study-guide/<guide_name>')
def study_guide(guide_name):
    content = load_study_guide(guide_name)
    if content:
        return render_template('study_guide.html', content=content, guide_name=guide_name)
    return "Study guide not found", 404

@app.route('/materials/quick-reference/<reference_name>')
def quick_reference(reference_name):
    content = load_quick_reference(reference_name)
    if content:
        return render_template('quick_reference.html', content=content, reference_name=reference_name)
    return "Reference material not found", 404

@app.route('/progress')
def progress():
    return render_template('progress.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
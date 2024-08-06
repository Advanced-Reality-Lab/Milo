class RunParams:
    def __init__(self, new_file_name = None, start_spliting_file = None, end_spliting_f0ile = None,
                 start_record_time = None, gpt = None, side = None, UPLOAD_FOLDER = None, audio_dir = None,
                 txt_dir = None, model = None, tokenizer = None, gpt_dir = None, session_dir = None,
                 out_udp_ip = None, out_udp_port = None, audio_name = None):

        self.audio_dir = audio_dir
        self.txt_dir = txt_dir
        self.audio_dir = audio_dir
        self.audio_name = audio_name
        self.out_udp_port = out_udp_port
        self.out_udp_ip = out_udp_ip
        self.session_dir = session_dir
        self.gpt_dir = gpt_dir
        self.txt_dir = txt_dir
        self.tokenizer = tokenizer
        self.model = model
        self.audio_dir = audio_dir

        self.audio_dir = audio_dir
        self.UPLOAD_FOLDER = UPLOAD_FOLDER
        self.side = side
        self.gpt = gpt
        self.start_record_time = start_record_time
        self.end_spliting_f0ile = end_spliting_f0ile
        self.start_spliting_file = start_spliting_file
        self.new_file_name = new_file_name
        self.audio_dir = audio_dir
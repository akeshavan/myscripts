__author__ = 'kjordan'

def dtitk_wf(subject_id, basedir):

    import nipype.interfaces.dipy as dipype
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import Function, IdentityInterface
    from nipype.interfaces.fsl.maths import Threshold, BinaryMaths

    #create input node
    inputspec = pe.Node(IdentityInterface(fields=['bvec_path', 'bval_path', 'diffdata']), name='inputspec')

    #create_dti_node
    dti_node = pe.Node(name= 'dti_node', interface=dipype.DTI())

    #create_thresh_node
    thresh_node = pe.Node(name='thresh_node', interface=Threshold())
    thresh_node.inputs.thresh = 0.15

    #create_binarize_node
    bin_node = pe.Node(name='bin_node', interface=BinaryMaths())

    #PUT ALL NODES TOGETHER INTO PIPELINE
    import nipype.interfaces.io as nio
    sinker = pe.Node(nio.DataSink(), name="sinker")
    sinker.inputs.base_directory = "/data/henry8/jordan/prepost/diffpype"
    sinker.inputs.container = subject_id

    pipeline = pe.Workflow(name='pipeline')
    pipeline.base_dir = basedir

   #connect nodes
    pipeline.connect(inputspec,'bvec_path', dti_node, 'in_bvec')
    pipeline.connect(inputspec,'bval_path', dti_node, 'in_bval')
    pipeline.connect(inputspec, 'diffdata', dti_node, 'in_file')

    pipeline.connect(dti_node, 'fa_file', thresh_node, 'in_file')
    pipeline.connect(thresh_node, 'out_file', bin_node, 'in_file')

    pipeline.connect(dti_node, 'out_file', sinker, 'dti.@tensor')
    pipeline.connect(dti_node, 'fa_file', sinker, 'dti.@fa')
    pipeline.connect(dti_node, 'md_file', sinker, 'dti.@md')
    pipeline.connect(dti_node, 'rd_file', sinker, 'dti.@rd')
    pipeline.connect(dti_node, 'ad_file', sinker, 'dti.@ad')
    pipeline.connect(thresh_node, 'out_file', sinker, 'dti.@fa_gtpt15')
    pipeline.connect(bin_node, 'out_file', sinker, 'dti.@mask_fa_gtpt15')

    pipeline.write_graph()
    pipeline.config["Execution"] = {"keep_inputs": True, "remove_unnecessary_outputs": False}

    return pipeline
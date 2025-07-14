# assume that the container already has activated the right environment
# asumme current working directory is at the top level of this repo
pip install --no-deps -e .
#cd /home/data/cimis-dash
#panel serve dash/head_calib_head_obs_nodes_cg.py dash/head_nodes_fg.py dash/head_obs_node_fg.py dash/trimesh_animator_cg.py dash/trimesh_animator_fg.py dash/trimesh_animator_fg_diff.py --address 0.0.0.0 --port 80 --allow-websocket-origin="*"  > panel.log.txt 2>&1
python dash/iwfm_dash.py
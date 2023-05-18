use bevy::{
    asset::{AssetLoader, LoadContext},
    prelude::*,
    render::{mesh::Indices, render_resource::PrimitiveTopology},
    utils::BoxedFuture,
};
#[derive(Reflect, Default, Component)]
#[reflect(Component)] // this tells the reflect derive to also reflect component behaviors
pub struct BlendGLBMeshLoader {
    path: String,
}

pub fn blend_glb_mesh_loader(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    query: Query<(&BlendGLBMeshLoader, Entity)>,
) {
    for (glbloader, entity) in query.iter() {
        println!("Loading Mesh {} for {:?}", glbloader.path, entity);
        commands.entity(entity).remove::<BlendGLBMeshLoader>();
        let mesh_handle: Handle<Mesh> = asset_server.load(glbloader.path.as_str());
        //        let mat_handle: Handle<StandardMaterial> =
        //            asset_server.load("scenes/proto2.scn.glb#Material0");
        commands.entity(entity).insert(mesh_handle);
        //commands.entity(entity).insert(mat_handle);
        //        "scenes/proto2.scn.glb#Material0"
    }
}

pub fn blend_glb_mesh_loaderP(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    query: Query<(&BlendGLBMeshLoader, Entity)>,
) {
    for (glbloader, entity) in query.iter() {
        println!("!!!Loading {} for {:?}", glbloader.path, entity);
        commands.entity(entity).remove::<BlendGLBMeshLoader>();
        //let mesh_handle: Handle<Mesh> = asset_server.load(glbloader.path.as_str());
        let test = PbrBundle {
            mesh: asset_server.load("scenes/proto2.scn.glb#Mesh1/Primitive0"),
            material: asset_server.load("scenes/proto2.scn.glb#Material1"),
            ..Default::default()
        };
        let test2 = PbrBundle {
            mesh: asset_server.load("scenes/proto2.scn.glb#Mesh0/Primitive0"),
            material: asset_server.load("scenes/proto2.scn.glb#Material0"),
            ..Default::default()
        };

        let mesh_handle: Handle<Mesh> = asset_server.load("scenes/proto2.scn.glb#Mesh0/Primitive0");
        let mat_handle: Handle<StandardMaterial> =
            asset_server.load("scenes/proto2.scn.glb#Material0");
        commands.entity(entity).insert(mesh_handle);
        commands.entity(entity).insert(mat_handle);
        //        commands.spawn(test2);
        //commands.entity(entity).insert(test.material);
    }
}

#[derive(Reflect, Default, Component)]
#[reflect(Component)] // this tells the reflect derive to also reflect component behaviors
pub struct BlendGLBMaterialLoader {
    path: String,
}

pub fn blend_glb_material_loader(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    query: Query<(&BlendGLBMaterialLoader, Entity)>,
) {
    for (glbloader, entity) in query.iter() {
        println!("Loading Material {} for {:?}", glbloader.path, entity);
        commands.entity(entity).remove::<BlendGLBMaterialLoader>();
        let material_handle: Handle<StandardMaterial> = asset_server.load(glbloader.path.as_str());
        commands.entity(entity).insert(material_handle);
    }
}
